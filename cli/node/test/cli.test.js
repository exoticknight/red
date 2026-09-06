import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { existsSync, mkdirSync, mkdtempSync, readFileSync, renameSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const cli = path.join(packageRoot, "src", "cli.js");
const releaseVersion = JSON.parse(readFileSync(path.join(packageRoot, "package.json"), "utf8")).version;

function run(args, cwd) {
  return execFileSync(process.execPath, [cli, ...args], {
    cwd,
    encoding: "utf8",
    stdio: ["ignore", "pipe", "pipe"],
  });
}

test("version reports the release and protocol versions as JSON", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-version-"));
  const result = JSON.parse(run(["version", "--json"], cwd));

  assert.deepEqual(result, {
    ok: true,
    protocolVersion: 1,
    releaseVersion,
  });
});

test("init creates a parseable project configuration", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-init-"));
  const result = JSON.parse(run(["init", "--json"], cwd));
  const config = readFileSync(path.join(cwd, "red.toml"), "utf8");

  assert.equal(result.ok, true);
  assert.equal(result.created, "red.toml");
  assert.match(config, /^version = 1/m);
  assert.match(config, /^paths = \["README\.md", "docs\/\*\*"\]/m);
  assert.match(config, /^path = "research"/m);
  assert.match(config, /^path = "evolve"/m);
});

test("new creates sequential research and evolve artifacts", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-new-"));
  run(["init", "--json"], cwd);

  const research = JSON.parse(
    run(["new", "research", "--title", "Tag semantics", "--json"], cwd),
  );
  const evolve = JSON.parse(
    run(
      [
        "new",
        "evolve",
        "--title",
        "Add tags",
        "--from",
        research.id,
        "--json",
      ],
      cwd,
    ),
  );

  assert.equal(research.id, "R-1");
  assert.equal(research.path, "research/R-1-tag-semantics.md");
  assert.equal(evolve.id, "E-1");
  assert.equal(evolve.path, "evolve/E-1-add-tags.md");
  assert.match(readFileSync(path.join(cwd, evolve.path), "utf8"), /based_on = \["R-1"\]/);
});

test("status counts artifacts and check rejects an unsupported protocol", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-status-"));
  run(["init", "--json"], cwd);
  run(["new", "research", "--title", "One", "--json"], cwd);
  run(["new", "evolve", "--title", "Two", "--json"], cwd);

  const status = JSON.parse(run(["status", "--json"], cwd));
  assert.deepEqual(status.counts, { document: 0, evolve: 1, research: 1 });

  const configFile = path.join(cwd, "red.toml");
  writeFileSync(
    configFile,
    readFileSync(configFile, "utf8").replace("version = 1", "version = 99"),
    "utf8",
  );
  assert.throws(
    () => run(["check", "--json"], cwd),
    (error) => {
      const payload = JSON.parse(error.stdout);
      return error.status === 1 && payload.ok === false && payload.errors.length === 1;
    },
  );
});

test("instructions preserve AGENTS content and remain idempotent", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-instructions-"));
  const agents = path.join(cwd, "AGENTS.md");
  writeFileSync(agents, "# Existing instructions\n", "utf8");

  run(["instructions", "install", "--target", "AGENTS.md", "--json"], cwd);
  run(["instructions", "install", "--target", "AGENTS.md", "--json"], cwd);
  run(["instructions", "export", "--output", "RED.md", "--json"], cwd);

  const installed = readFileSync(agents, "utf8");
  assert.match(installed, /^# Existing instructions/m);
  assert.equal(installed.match(/<!-- red:start protocol=1 -->/g).length, 1);
  assert.match(readFileSync(path.join(cwd, "RED.md"), "utf8"), /^# RED Agent Instructions/m);
});

test("skill installs into repository scope with release metadata", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-skill-"));
  const result = JSON.parse(
    run(["skill", "install", "--scope", "repo", "--json"], cwd),
  );
  const installed = path.join(cwd, ".agents", "skills", "red");

  assert.equal(result.path, ".agents/skills/red");
  assert.match(readFileSync(path.join(installed, "SKILL.md"), "utf8"), /name: red/);
  assert.deepEqual(
    JSON.parse(readFileSync(path.join(installed, ".red-install.json"), "utf8")),
    { distribution: "red", protocolVersion: 1, releaseVersion },
  );
});

test("skill reports, updates, and uninstalls only managed installations", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-skill-lifecycle-"));
  run(["skill", "install", "--scope", "repo", "--json"], cwd);

  const status = JSON.parse(run(["skill", "status", "--scope", "repo", "--json"], cwd));
  assert.equal(status.installed, true);
  assert.equal(status.releaseVersion, releaseVersion);

  const skillFile = path.join(cwd, ".agents", "skills", "red", "SKILL.md");
  writeFileSync(skillFile, "changed", "utf8");
  run(["skill", "update", "--scope", "repo", "--json"], cwd);
  assert.match(readFileSync(skillFile, "utf8"), /name: red/);

  run(["skill", "uninstall", "--scope", "repo", "--json"], cwd);
  assert.equal(existsSync(path.dirname(skillFile)), false);
});

test("instructions can remove only their managed block", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-instruction-remove-"));
  writeFileSync(path.join(cwd, "AGENTS.md"), "# Existing\n", "utf8");
  run(["instructions", "install", "--json"], cwd);
  run(["instructions", "uninstall", "--json"], cwd);
  assert.equal(readFileSync(path.join(cwd, "AGENTS.md"), "utf8"), "# Existing\n");
});

test("promote creates an evolve item then records document synchronization", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-promote-"));
  run(["init", "--json"], cwd);
  const research = JSON.parse(run(["new", "research", "--title", "Need policy", "--json"], cwd));
  const evolve = JSON.parse(
    run(["promote", research.id, "--to", "evolve", "--title", "Adopt policy", "--json"], cwd),
  );
  writeFileSync(path.join(cwd, "README.md"), "# Project\n", "utf8");
  const evolveFile = path.join(cwd, evolve.path);
  writeFileSync(
    evolveFile,
    `${readFileSync(evolveFile, "utf8")}\n\`\`\`toml\nverified = false\ndocument_paths = ["body.md"]\n\`\`\`\n`,
    "utf8",
  );
  const accepted = JSON.parse(
    run(["promote", evolve.id, "--to", "document", "--accepted", "--verified", "--document", "README.md", "--json"], cwd),
  );

  assert.equal(evolve.id, "E-1");
  assert.equal(accepted.status, "accepted");
  const content = readFileSync(evolveFile, "utf8");
  assert.match(content, /status = "accepted"/);
  assert.match(content, /verified = true/);
  assert.match(content, /document_paths = \["README.md"\]/);
  assert.match(content, /verified = false\ndocument_paths = \["body.md"\]/);
});

test("check validates artifact identities and references", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-check-artifacts-"));
  run(["init", "--json"], cwd);
  mkdirSync(path.join(cwd, "evolve"));
  const evolve = { path: "evolve/E-1-broken-reference.md" };
  writeFileSync(
    path.join(cwd, evolve.path),
    '+++\nid = "E-1"\nstate = "evolve"\nstatus = "open"\ntitle = "Broken reference"\ncreated = "2026-09-05"\nbased_on = ["R-9999"]\n+++\n',
    "utf8",
  );
  const invalid = (() => {
    try {
      run(["check", "--json"], cwd);
    } catch (error) {
      return JSON.parse(error.stdout);
    }
  })();
  assert.match(invalid.errors.join("\n"), /unknown artifact R-9999/);

  const file = path.join(cwd, evolve.path);
  writeFileSync(file, readFileSync(file, "utf8").replace('id = "E-1"', 'id = "R-1"'), "utf8");
  const mismatched = (() => {
    try {
      run(["check", "--json"], cwd);
    } catch (error) {
      return JSON.parse(error.stdout);
    }
  })();
  assert.match(mismatched.errors.join("\n"), /does not match evolve state/);
});

test("configuration paths cannot escape the project root", () => {
  const base = mkdtempSync(path.join(tmpdir(), "red-node-path-safety-"));
  const cwd = path.join(base, "project");
  mkdirSync(cwd);
  run(["init", "--json"], cwd);
  const configFile = path.join(cwd, "red.toml");
  writeFileSync(
    configFile,
    readFileSync(configFile, "utf8").replace('path = "research"', 'path = "../escaped"'),
    "utf8",
  );

  assert.throws(() => run(["new", "research", "--title", "Unsafe", "--json"], cwd));
  assert.equal(existsSync(path.join(base, "escaped")), false);
});

test("new rejects references to artifacts that do not exist", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-reference-safety-"));
  run(["init", "--json"], cwd);

  assert.throws(() =>
    run(["new", "evolve", "--title", "Invalid", "--from", "R-9999", "--json"], cwd),
  );
  assert.equal(existsSync(path.join(cwd, "evolve")), false);
});

test("instructions refuse a malformed managed block without changing user content", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-marker-safety-"));
  const agents = path.join(cwd, "AGENTS.md");
  const original = "# Existing\n\n<!-- red:start protocol=1 -->\nUser-owned content\n";
  writeFileSync(agents, original, "utf8");

  assert.throws(() => run(["instructions", "install", "--json"], cwd));
  assert.equal(readFileSync(agents, "utf8"), original);
});

test("promotion rejects a Document path that escapes the project", () => {
  const base = mkdtempSync(path.join(tmpdir(), "red-node-document-safety-"));
  const cwd = path.join(base, "project");
  mkdirSync(cwd);
  run(["init", "--json"], cwd);
  const research = JSON.parse(run(["new", "research", "--title", "Source", "--json"], cwd));
  const evolve = JSON.parse(run(["promote", research.id, "--to", "evolve", "--json"], cwd));
  writeFileSync(path.join(base, "outside.md"), "# Outside\n", "utf8");

  assert.throws(() =>
    run(["promote", evolve.id, "--to", "document", "--accepted", "--verified", "--document", "docs/../../outside.md", "--json"], cwd),
  );
  assert.match(readFileSync(path.join(cwd, evolve.path), "utf8"), /status = "open"/);
});

test("renaming an artifact cannot cause identifier reuse", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-id-safety-"));
  run(["init", "--json"], cwd);
  const research = JSON.parse(run(["new", "research", "--title", "First", "--json"], cwd));
  renameSync(path.join(cwd, research.path), path.join(cwd, "research", "renamed.md"));

  assert.throws(() => run(["new", "research", "--title", "Second", "--json"], cwd));
});

test("check enforces required configuration policy", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-config-schema-"));
  run(["init", "--json"], cwd);
  const configFile = path.join(cwd, "red.toml");
  writeFileSync(configFile, readFileSync(configFile, "utf8").replace(/\n\[policy\][\s\S]*$/, "\n"), "utf8");

  assert.throws(
    () => run(["check", "--json"], cwd),
    (error) => error.status === 1 && JSON.parse(error.stdout).errors.some((item) => item.includes("policy")),
  );
});

test("mutations reject invalid prospective artifact metadata before writing", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-prospective-schema-"));
  run(["init", "--json"], cwd);

  assert.throws(() => run(["new", "research", "--title", "", "--json"], cwd));
  assert.equal(existsSync(path.join(cwd, "research")), false);

  const source = JSON.parse(run(["new", "research", "--title", "Source", "--json"], cwd));
  assert.throws(() =>
    run(["new", "evolve", "--title", "Duplicate", "--from", source.id, source.id, "--json"], cwd),
  );
  assert.equal(existsSync(path.join(cwd, "evolve")), false);

  const evolve = JSON.parse(run(["promote", source.id, "--to", "evolve", "--json"], cwd));
  writeFileSync(path.join(cwd, "README.md"), "# Project\n", "utf8");
  assert.throws(() =>
    run([
      "promote", evolve.id, "--to", "document", "--accepted", "--verified",
      "--document", "README.md", "README.md", "--json",
    ], cwd),
  );
  assert.match(readFileSync(path.join(cwd, evolve.path), "utf8"), /status = "open"/);
});

test("identifier allocation crosses four digits", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-unbounded-id-"));
  run(["init", "--json"], cwd);
  mkdirSync(path.join(cwd, "research"));
  writeFileSync(
    path.join(cwd, "research", "R-9999-last.md"),
    '+++\nid = "R-9999"\nstate = "research"\nstatus = "open"\ntitle = "Last"\ncreated = "2026-09-06"\n+++\n',
    "utf8",
  );

  const created = JSON.parse(run(["new", "research", "--title", "Beyond four digits", "--json"], cwd));

  assert.equal(created.id, "R-10000");
  assert.equal(created.path, "research/R-10000-beyond-four-digits.md");
});

test("check rejects calendar-invalid creation dates", () => {
  const cwd = mkdtempSync(path.join(tmpdir(), "red-node-date-schema-"));
  run(["init", "--json"], cwd);
  mkdirSync(path.join(cwd, "research"));
  writeFileSync(
    path.join(cwd, "research", "R-1-impossible.md"),
    '+++\nid = "R-1"\nstate = "research"\nstatus = "open"\ntitle = "Impossible"\ncreated = "2026-02-31"\n+++\n',
    "utf8",
  );

  assert.throws(
    () => run(["check", "--json"], cwd),
    (error) => error.status === 1 && JSON.parse(error.stdout).errors.some(
      (item) => item.startsWith("RED_SCHEMA_FORMAT ") && item.endsWith("/created"),
    ),
  );
});
