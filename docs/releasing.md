# Releasing

1. Update `CHANGELOG.md` and ensure the intended source version is represented consistently.
2. Run all checks in `CONTRIBUTING.md`.
3. Create and push an annotated `vMAJOR.MINOR.PATCH` tag.
4. The tag workflow builds the npm package, Python wheel and source distribution, plugin archive, and standalone Skill archive.
5. Protected publish jobs use npm and PyPI trusted publishing. A final job creates the GitHub Release only after both registries succeed.

Configure the GitHub repository before the first release:

- Add trusted publisher records for `@exoticknight/red` on npm and `red-methodology` on PyPI.
- Protect the `pypi` and `npm` environments if release approval is required.
- Grant the workflow `id-token: write` only in publish jobs and `contents: write` only in the release job.

The plugin archive is attached to the GitHub Release. Submission to a public plugin marketplace is a separate review process; the source plugin remains installable directly from this repository.
