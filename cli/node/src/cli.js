#!/usr/bin/env node

import {
  cpSync,
  existsSync,
  mkdirSync,
  readFileSync,
  realpathSync,
  readdirSync,
  renameSync,
  rmSync,
  writeFileSync,
} from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { isDeepStrictEqual } from "node:util";
import { Command } from "commander";
import Ajv2020 from "ajv/dist/2020.js";
import addFormats from "ajv-formats";
import { parse, stringify } from "smol-toml";

const packageRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const packageMetadata = JSON.parse(
  readFileSync(path.join(packageRoot, "package.json"), "utf8"),
);
const protocolVersion = 1;
const redStartMarker = `<!-- red:start protocol=${protocolVersion} -->`;
const redEndMarker = "<!-- red:end -->";

function loadProtocolSchema(name) {
  const candidates = [
    path.join(packageRoot, "bundled", "protocol", `${name}-schema.json`),
    path.resolve(packageRoot, "..", "..", "spec", `${name}-schema.json`),
  ];
  const source = candidates.find((candidate) => existsSync(candidate));
  if (!source) throw new Error(`Bundled RED ${name} schema is missing`);
  return JSON.parse(readFileSync(source, "utf8"));
}

const schemaCompiler = new Ajv2020({ allErrors: true });
addFormats(schemaCompiler);
const validateConfigSchema = schemaCompiler.compile(loadProtocolSchema("config"));
const validateArtifactSchema = schemaCompiler.compile(loadProtocolSchema("artifact"));

function pointerSegment(value) {
  return String(value).replaceAll("~", "~0").replaceAll("/", "~1");
}

function normalizedSchemaErrors(prefix, errors = []) {
  return [...new Set(errors.flatMap((error) => {
    if (error.keyword === "if") return [];
    let location = `${prefix}${error.instancePath}`;
    if (error.keyword === "required") {
      location += `/${pointerSegment(error.params.missingProperty)}`;
    } else if (error.keyword === "additionalProperties") {
      location += `/${pointerSegment(error.params.additionalProperty)}`;
    }
    const keyword = error.keyword.replace(/([a-z])([A-Z])/g, "$1_$2").toUpperCase();
    return [`RED_SCHEMA_${keyword} ${location || "/"}`];
  }))].sort();
}

const defaultConfig = `version = 1

[document]
paths = ["README.md", "docs/**"]

[research]
path = "research"

[evolve]
path = "evolve"

[policy]
document_requires_approval = true
report_document_implementation_conflicts = true
`;

function print(payload, json, message) {
  process.stdout.write(`${json ? JSON.stringify(payload) : message}\n`);
}

function relativePath(root, target) {
  return path.relative(root, target).replaceAll(path.sep, "/");
}

function loadConfig(root = process.cwd()) {
  return parse(readFileSync(path.join(root, "red.toml"), "utf8"), {
    integersAsBigInt: "asNeeded",
  });
}

function isProjectRelative(root, configuredPath) {
  if (typeof configuredPath !== "string" || configuredPath.length === 0 || path.isAbsolute(configuredPath)) {
    return false;
  }
  const base = configuredPath.endsWith("/**") ? configuredPath.slice(0, -3) : configuredPath;
  const rootPath = realpathSync(root);
  const candidate = path.resolve(root, base);
  let ancestor = candidate;
  const missing = [];
  while (!existsSync(ancestor)) {
    const parent = path.dirname(ancestor);
    if (parent === ancestor) return false;
    missing.unshift(path.basename(ancestor));
    ancestor = parent;
  }
  const targetPath = path.resolve(realpathSync(ancestor), ...missing);
  const relative = path.relative(rootPath, targetPath);
  return relative === "" || (!relative.startsWith(`..${path.sep}`) && relative !== ".." && !path.isAbsolute(relative));
}

function validateConfig(root = process.cwd()) {
  let config;
  try {
    config = loadConfig(root);
  } catch (error) {
    return { errors: [`Cannot read red.toml: ${error.message}`] };
  }
  if (typeof config.version === "bigint") {
    if (config.version < 1n) {
      return { config, errors: ["RED_SCHEMA_MINIMUM red.toml/version"] };
    }
    if (config.version > BigInt(Number.MAX_SAFE_INTEGER)) {
      return { config, errors: ["RED_SCHEMA_MAXIMUM red.toml/version"] };
    }
    config.version = Number(config.version);
  }
  const errors = [];
  if (!validateConfigSchema(config)) {
    errors.push(...normalizedSchemaErrors("red.toml", validateConfigSchema.errors));
  }
  if (errors.length > 0) return { config, errors };
  if (config.version !== protocolVersion) {
    return {
      config,
      errors: [
        `Unsupported RED protocol; expected ${protocolVersion}`,
      ],
    };
  }
  if (Array.isArray(config.document?.paths)) {
    for (const documentPath of config.document.paths) {
      if (!isProjectRelative(root, documentPath)) {
        errors.push(`document path must stay within the project: ${String(documentPath)}`);
      }
    }
  }
  for (const state of ["research", "evolve"]) {
    if (typeof config[state]?.path === "string" && !isProjectRelative(root, config[state].path)) {
      errors.push(`${state}.path must stay within the project`);
    }
  }
  return { config, errors };
}

function readArtifact(file, expectedState) {
  const content = readFileSync(file, "utf8");
  const match = content.match(/^\+\+\+\r?\n([\s\S]*?)\r?\n\+\+\+(?:\r?\n|$)/);
  if (!match) throw new Error(`${file} has no TOML frontmatter`);
  const metadata = parse(match[1]);
  return { content, file, metadata, expectedState };
}

function replaceArtifactFrontmatter(content, metadata) {
  const match = content.match(/^\+\+\+\r?\n[\s\S]*?\r?\n\+\+\+(?:\r?\n|$)/);
  if (!match) throw new Error("Artifact has no TOML frontmatter");
  const ordered = {};
  for (const key of [
    "id",
    "state",
    "status",
    "title",
    "created",
    "based_on",
    "document_paths",
    "verified",
  ]) {
    if (Object.hasOwn(metadata, key)) ordered[key] = metadata[key];
  }
  const canonical = stringify(ordered)
    .trimEnd()
    .replaceAll("[ ", "[")
    .replaceAll(" ]", "]");
  const trailingNewline = /\r?\n$/.test(match[0]) ? "\n" : "";
  return `+++\n${canonical}\n+++${trailingNewline}${content.slice(match[0].length)}`;
}

function projectArtifacts(root, config) {
  return ["research", "evolve"].flatMap((state) =>
    markdownFiles(path.resolve(root, config[state].path)).map((file) => {
      try {
        return { artifact: readArtifact(file, state) };
      } catch (error) {
        return { error: `${relativePath(root, file)}: ${error.message}` };
      }
    }),
  );
}

function validateArtifacts(root, config) {
  const entries = projectArtifacts(root, config);
  const errors = entries.filter((entry) => entry.error).map((entry) => entry.error);
  const artifacts = entries.filter((entry) => entry.artifact).map((entry) => entry.artifact);
  const identifiers = new Map();
  for (const artifact of artifacts) {
    const { id, state } = artifact.metadata;
    const expectedPrefix = artifact.expectedState === "research" ? "R" : "E";
    const displayPath = relativePath(root, artifact.file);
    if (!validateArtifactSchema(artifact.metadata)) {
      errors.push(
        ...normalizedSchemaErrors(displayPath, validateArtifactSchema.errors),
      );
    }
    if (state !== artifact.expectedState || typeof id !== "string" || !new RegExp(`^${expectedPrefix}-(?:[1-9]\\d*|0\\d{3})$`).test(id)) {
      errors.push(`${displayPath}: identity does not match ${artifact.expectedState} state`);
    }
    if (typeof id === "string" && !path.basename(artifact.file).startsWith(`${id}-`)) {
      errors.push(`${displayPath}: filename must start with ${id}-`);
    }
    if (typeof id === "string") {
      if (identifiers.has(id)) errors.push(`${displayPath}: duplicate artifact id ${id}`);
      identifiers.set(id, artifact);
    }
  }
  for (const artifact of artifacts) {
    const references = artifact.metadata.based_on ?? [];
    if (!Array.isArray(references)) {
      errors.push(`${relativePath(root, artifact.file)}: based_on must be an array`);
      continue;
    }
    for (const reference of references) {
      if (!identifiers.has(reference)) {
        errors.push(`${relativePath(root, artifact.file)}: unknown artifact ${reference}`);
      }
    }
    const documentPaths = artifact.metadata.document_paths ?? [];
    if (Array.isArray(documentPaths)) {
      for (const documentPath of documentPaths) {
        if (
          !isProjectRelative(root, documentPath) ||
          !acceptsDocumentPath(root, documentPath, config.document.paths) ||
          !existsSync(path.resolve(root, documentPath))
        ) {
          errors.push(`${relativePath(root, artifact.file)}: invalid Document path ${String(documentPath)}`);
        }
      }
    }
  }
  return { artifacts, errors };
}

function markdownFiles(directory) {
  if (!existsSync(directory)) return [];
  return readdirSync(directory, { withFileTypes: true })
    .sort((left, right) => Buffer.compare(Buffer.from(left.name), Buffer.from(right.name)))
    .flatMap((entry) => {
    const target = path.join(directory, entry.name);
    if (entry.isDirectory()) return markdownFiles(target);
    return entry.isFile() && entry.name.endsWith(".md") ? [target] : [];
    });
}

function documentCount(root, patterns) {
  const found = new Set();
  for (const pattern of patterns) {
    if (pattern.endsWith("/**")) {
      for (const file of markdownFiles(path.join(root, pattern.slice(0, -3)))) {
        found.add(path.resolve(file));
      }
    } else {
      const target = path.join(root, pattern);
      if (existsSync(target)) found.add(path.resolve(target));
    }
  }
  return found.size;
}

function slugify(value) {
  const slug = value
    .normalize("NFKC")
    .toLocaleLowerCase("en")
    .replace(/[^\p{Letter}\p{Number}]+/gu, "-")
    .replace(/^-+|-+$/g, "");
  return slug || "untitled";
}

function nextIdentifier(artifacts, prefix) {
  let highest = 0n;
  for (const artifact of artifacts) {
    const match = artifact.metadata.id?.match(new RegExp(`^${prefix}-((?:[1-9]\\d*)|(?:0\\d{3}))$`));
    if (match) {
      const value = BigInt(match[1]);
      if (value > highest) highest = value;
    }
  }
  return `${prefix}-${highest + 1n}`;
}

function localDate() {
  const now = new Date();
  return [now.getFullYear(), now.getMonth() + 1, now.getDate()]
    .map((part, index) => (index === 0 ? String(part) : String(part).padStart(2, "0")))
    .join("-");
}

function renderArtifact(state, id, title, basedOn, created) {
  const metadata = {
    id,
    state,
    status: "open",
    title,
    created,
  };
  if (basedOn.length > 0) metadata.based_on = basedOn;
  const sections =
    state === "research"
      ? ["Question", "Evidence", "Unknowns"]
      : ["Change", "Rationale", "Acceptance", "Open questions"];
  const body = sections.map((section) => `## ${section}\n\n`).join("");
  const canonicalMetadata = stringify(metadata)
    .trimEnd()
    .replaceAll("[ ", "[")
    .replaceAll(" ]", "]");
  return `+++\n${canonicalMetadata}\n+++\n\n# ${id}: ${title}\n\n${body}`;
}

function createArtifact(state, title, basedOn, root = process.cwd()) {
  if (!new Set(["research", "evolve"]).has(state)) {
    throw new Error("state must be research or evolve");
  }
  const { config, errors } = validateConfig(root);
  if (errors.length > 0) throw new Error(errors.join("; "));
  const validation = validateArtifacts(root, config);
  if (validation.errors.length > 0) throw new Error(validation.errors.join("; "));
  if (basedOn.length > 0) {
    const identifiers = new Set(validation.artifacts.map((artifact) => artifact.metadata.id));
    const unknown = basedOn.filter((identifier) => !identifiers.has(identifier));
    if (unknown.length > 0) throw new Error(`Unknown source artifact: ${unknown.join(", ")}`);
  }
  const prefix = state === "research" ? "R" : "E";
  const id = nextIdentifier(validation.artifacts, prefix);
  const created = localDate();
  const metadata = { id, state, status: "open", title, created };
  if (basedOn.length > 0) metadata.based_on = basedOn;
  if (!validateArtifactSchema(metadata)) {
    throw new Error(normalizedSchemaErrors(id, validateArtifactSchema.errors).join("; "));
  }
  const directory = path.resolve(root, config[state].path);
  mkdirSync(directory, { recursive: true });
  const destination = path.join(directory, `${id}-${slugify(title)}.md`);
  writeFileSync(destination, renderArtifact(state, id, title, basedOn, created), {
    encoding: "utf8",
    flag: "wx",
  });
  return { ok: true, id, path: relativePath(root, destination), state };
}

function skillSource() {
  const candidates = [
    path.join(packageRoot, "bundled", "skill", "red"),
    path.resolve(packageRoot, "..", "..", "plugins", "red", "skills", "red"),
  ];
  const source = candidates.find((candidate) =>
    existsSync(path.join(candidate, "SKILL.md")),
  );
  if (!source) throw new Error("Bundled RED Skill is missing from this distribution");
  return source;
}

function skillAsset(name) {
  const asset = path.join(skillSource(), "assets", name);
  if (!existsSync(asset)) throw new Error(`Bundled RED asset is missing: ${name}`);
  return readFileSync(asset, "utf8");
}

function installInstructions(target, root = process.cwd()) {
  const destination = path.resolve(root, target);
  const fragment = skillAsset("AGENTS.fragment.md").trimEnd();
  const current = existsSync(destination) ? readFileSync(destination, "utf8") : "";
  const start = current.indexOf(redStartMarker);
  const end = current.indexOf(redEndMarker, Math.max(start, 0));
  if (
    (start >= 0) !== (end >= 0) ||
    (start >= 0 && current.indexOf(redStartMarker, start + redStartMarker.length) >= 0) ||
    (end >= 0 && current.indexOf(redEndMarker, end + redEndMarker.length) >= 0)
  ) {
    throw new Error("Managed RED instructions block is malformed; refusing to modify it");
  }
  let updated;
  if (start >= 0 && end >= start) {
    updated = `${current.slice(0, start)}${fragment}${current.slice(end + redEndMarker.length)}`;
  } else {
    updated = `${current.trimEnd()}${current.trimEnd() ? "\n\n" : ""}${fragment}\n`;
  }
  mkdirSync(path.dirname(destination), { recursive: true });
  writeFileSync(destination, updated, "utf8");
  return { ok: true, path: relativePath(root, destination), protocolVersion };
}

function uninstallInstructions(target, root = process.cwd()) {
  const destination = path.resolve(root, target);
  if (!existsSync(destination)) throw new Error(`Instructions file does not exist: ${target}`);
  const current = readFileSync(destination, "utf8");
  const start = current.indexOf(redStartMarker);
  const end = current.indexOf(redEndMarker, Math.max(start, 0));
  if (
    start < 0 ||
    end < start ||
    current.indexOf(redStartMarker, start + redStartMarker.length) >= 0 ||
    current.indexOf(redEndMarker, end + redEndMarker.length) >= 0
  ) {
    throw new Error("Exactly one complete managed RED instructions block is required");
  }
  const remaining = `${current.slice(0, start)}${current.slice(end + redEndMarker.length)}`.trimEnd();
  writeFileSync(destination, remaining ? `${remaining}\n` : "", "utf8");
  return { ok: true, path: relativePath(root, destination), protocolVersion };
}

function skillDestination(scope, root = process.cwd()) {
  return scope === "repo"
    ? path.resolve(root, ".agents", "skills", "red")
    : path.resolve(process.env.USERPROFILE ?? process.env.HOME ?? "", ".agents", "skills", "red");
}

function managedSkillMetadata(destination) {
  const metadataFile = path.join(destination, ".red-install.json");
  if (!existsSync(metadataFile)) throw new Error(`No managed RED Skill at ${destination}`);
  const metadata = JSON.parse(readFileSync(metadataFile, "utf8"));
  if (metadata.distribution !== "red") throw new Error(`Refusing to modify unmanaged Skill at ${destination}`);
  return metadata;
}

function installSkill(scope, root = process.cwd()) {
  const destination = skillDestination(scope, root);
  if (existsSync(destination)) throw new Error(`RED Skill already exists at ${destination}`);
  writeSkill(destination);
  return { ok: true, path: scope === "repo" ? ".agents/skills/red" : destination, scope };
}

function writeSkill(destination) {
  mkdirSync(path.dirname(destination), { recursive: true });
  cpSync(skillSource(), destination, { recursive: true, errorOnExist: true });
  writeFileSync(
    path.join(destination, ".red-install.json"),
    `${JSON.stringify({
      distribution: "red",
      protocolVersion,
      releaseVersion: packageMetadata.version,
    }, null, 2)}\n`,
    "utf8",
  );
}

function updateSkill(scope, root = process.cwd()) {
  const destination = skillDestination(scope, root);
  managedSkillMetadata(destination);
  const nonce = `${process.pid}-${Date.now()}`;
  const staging = `${destination}.red-stage-${nonce}`;
  const backup = `${destination}.red-backup-${nonce}`;
  try {
    writeSkill(staging);
    renameSync(destination, backup);
    try {
      renameSync(staging, destination);
    } catch (error) {
      renameSync(backup, destination);
      throw error;
    }
    rmSync(backup, { recursive: true });
  } catch (error) {
    if (existsSync(staging)) rmSync(staging, { recursive: true });
    throw error;
  }
  return { ok: true, path: scope === "repo" ? ".agents/skills/red" : destination, scope };
}

function findArtifact(root, identifier, config) {
  const { artifacts, errors } = validateArtifacts(root, config);
  if (errors.length > 0) throw new Error(errors.join("; "));
  const resolved = path.resolve(root, identifier);
  const artifact = existsSync(resolved)
    ? artifacts.find((candidate) => path.resolve(candidate.file) === resolved)
    : artifacts.find((candidate) => candidate.metadata.id === identifier);
  if (!artifact) throw new Error(`Artifact not found: ${identifier}`);
  return artifact;
}

function acceptsDocumentPath(root, documentPath, patterns) {
  if (!isProjectRelative(root, documentPath)) return false;
  const normalized = documentPath.replaceAll("\\", "/");
  return patterns.some((pattern) =>
    pattern.endsWith("/**") ? normalized.startsWith(pattern.slice(0, -2)) : normalized === pattern,
  );
}

function acceptIntoDocument(root, artifact, documentPaths, config, accepted, verified) {
  if (artifact.expectedState !== "evolve") throw new Error("Only Evolve artifacts can promote to Document");
  if (!accepted || !verified) {
    throw new Error("Document promotion requires explicit --accepted and --verified assertions");
  }
  if (documentPaths.length === 0) throw new Error("At least one --document path is required");
  for (const documentPath of documentPaths) {
    if (!acceptsDocumentPath(root, documentPath, config.document.paths)) {
      throw new Error(`${documentPath} is not declared by document.paths`);
    }
    if (!existsSync(path.resolve(root, documentPath))) {
      throw new Error(`Document does not exist: ${documentPath}`);
    }
  }
  const prospective = {
    ...artifact.metadata,
    status: "accepted",
    verified: true,
    document_paths: documentPaths,
  };
  if (!validateArtifactSchema(prospective)) {
    throw new Error(
      normalizedSchemaErrors(artifact.metadata.id, validateArtifactSchema.errors).join("; "),
    );
  }
  const updated = replaceArtifactFrontmatter(artifact.content, prospective);
  const finalMatch = updated.match(/^\+\+\+\n([\s\S]*?)\n\+\+\+(?:\n|$)/);
  const finalMetadata = finalMatch ? parse(finalMatch[1]) : null;
  if (
    !finalMetadata ||
    !isDeepStrictEqual(finalMetadata, prospective) ||
    !validateArtifactSchema(finalMetadata)
  ) {
    throw new Error("Refusing to write invalid promoted artifact metadata");
  }
  writeFileSync(artifact.file, updated, "utf8");
  return {
    ok: true,
    id: artifact.metadata.id,
    path: relativePath(root, artifact.file),
    state: "document",
    status: "accepted",
    documentPaths,
  };
}

const program = new Command();
program.name("red").description("Deterministic operations for the RED methodology");
program.exitOverride();

program
  .command("version")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const payload = {
      ok: true,
      protocolVersion,
      releaseVersion: packageMetadata.version,
    };
    print(
      payload,
      options.json,
      `RED ${payload.releaseVersion} (protocol ${payload.protocolVersion})`,
    );
  });

program
  .command("init")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const destination = path.resolve("red.toml");
    writeFileSync(destination, defaultConfig, { encoding: "utf8", flag: "wx" });
    const payload = { ok: true, created: "red.toml", protocolVersion };
    print(payload, options.json, "Created red.toml");
  });

program
  .command("new <state>")
  .requiredOption("--title <title>", "artifact title")
  .option("--from <id...>", "source research or evolve identifiers", [])
  .option("--json", "emit machine-readable output")
  .action((state, options) => {
    const payload = createArtifact(state, options.title, options.from);
    print(payload, options.json, `Created ${payload.id} at ${payload.path}`);
  });

program
  .command("promote <artifact>")
  .requiredOption("--to <state>", "target state: evolve or document")
  .option("--title <title>", "title for a new Evolve artifact")
  .option("--document <path...>", "synchronized Document paths", [])
  .option("--accepted", "assert that the Evolve proposal was accepted")
  .option("--verified", "assert that implementation and Document were verified")
  .option("--json", "emit machine-readable output")
  .action((identifier, options) => {
    const root = process.cwd();
    const { config, errors } = validateConfig(root);
    if (errors.length > 0) throw new Error(errors.join("; "));
    const artifact = findArtifact(root, identifier, config);
    let payload;
    if (options.to === "evolve") {
      if (artifact.expectedState !== "research") throw new Error("Only Research artifacts can promote to Evolve");
      payload = createArtifact("evolve", options.title ?? artifact.metadata.title, [artifact.metadata.id], root);
    } else if (options.to === "document") {
      payload = acceptIntoDocument(
        root,
        artifact,
        options.document,
        config,
        options.accepted,
        options.verified,
      );
    } else {
      throw new Error("target state must be evolve or document");
    }
    print(payload, options.json, `Promoted ${identifier} to ${options.to}`);
  });

program
  .command("status")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const root = process.cwd();
    const { config, errors } = validateConfig(root);
    if (errors.length > 0) throw new Error(errors.join("; "));
    const payload = {
      ok: true,
      protocolVersion,
      counts: {
        document: documentCount(root, config.document.paths),
        evolve: markdownFiles(path.join(root, config.evolve.path)).length,
        research: markdownFiles(path.join(root, config.research.path)).length,
      },
    };
    print(
      payload,
      options.json,
      `Document: ${payload.counts.document}, Evolve: ${payload.counts.evolve}, Research: ${payload.counts.research}`,
    );
  });

program
  .command("check")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const root = process.cwd();
    const validation = validateConfig(root);
    const errors = [...validation.errors];
    if (validation.config && errors.length === 0) {
      errors.push(...validateArtifacts(root, validation.config).errors);
    }
    const payload = { ok: errors.length === 0, errors, protocolVersion };
    print(
      payload,
      options.json,
      payload.ok ? "RED project is valid" : errors.join("\n"),
    );
    if (!payload.ok) process.exitCode = 1;
  });

const instructions = program
  .command("instructions")
  .description("Manage lightweight RED agent instructions");

instructions
  .command("install")
  .option("--target <path>", "instructions file to update", "AGENTS.md")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const payload = installInstructions(options.target);
    print(payload, options.json, `Installed RED instructions in ${payload.path}`);
  });

instructions
  .command("uninstall")
  .option("--target <path>", "instructions file to update", "AGENTS.md")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const payload = uninstallInstructions(options.target);
    print(payload, options.json, `Removed RED instructions from ${payload.path}`);
  });

instructions
  .command("export")
  .option("--output <path>", "standalone instructions file", "RED.md")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    const destination = path.resolve(options.output);
    writeFileSync(destination, skillAsset("RED.md"), { encoding: "utf8", flag: "wx" });
    const payload = { ok: true, path: relativePath(process.cwd(), destination), protocolVersion };
    print(payload, options.json, `Exported RED instructions to ${payload.path}`);
  });

const skill = program.command("skill").description("Manage the RED Skill");

skill
  .command("install")
  .option("--scope <scope>", "installation scope: repo or user", "repo")
  .option("--json", "emit machine-readable output")
  .action((options) => {
    if (!new Set(["repo", "user"]).has(options.scope)) {
      throw new Error("scope must be repo or user");
    }
    const payload = installSkill(options.scope);
    print(payload, options.json, `Installed RED Skill at ${payload.path}`);
  });

for (const action of ["status", "update", "uninstall"]) {
  skill
    .command(action)
    .option("--scope <scope>", "installation scope: repo or user", "repo")
    .option("--json", "emit machine-readable output")
    .action((options) => {
      if (!new Set(["repo", "user"]).has(options.scope)) throw new Error("scope must be repo or user");
      const destination = skillDestination(options.scope);
      const metadata = managedSkillMetadata(destination);
      let payload;
      if (action === "status") {
        payload = { ok: true, installed: true, path: options.scope === "repo" ? ".agents/skills/red" : destination, ...metadata };
      } else if (action === "update") {
        payload = updateSkill(options.scope);
      } else {
        rmSync(destination, { recursive: true });
        payload = { ok: true, removed: true, path: options.scope === "repo" ? ".agents/skills/red" : destination, scope: options.scope };
      }
      print(payload, options.json, `${action} completed for ${payload.path}`);
    });
}

program.parseAsync(process.argv).catch((error) => {
  if (typeof error.code === "string" && error.code.startsWith("commander.")) {
    process.exitCode = error.exitCode === 0 ? 0 : 2;
  } else {
    process.stderr.write(`${error.message}\n`);
    process.exitCode = 2;
  }
});
