# Releasing MSNSwitch

HACS uses **GitHub Releases** (not tags alone). Each release should ship a zip asset named `msnswitch.zip` (handled automatically by the release workflow).

## Steps for a new version

1. **Bump version** in `custom_components/msnswitch/manifest.json` (e.g. `1.0.1`).
2. **Commit and push** to `main`.
3. **Create a GitHub release** with a tag matching the version:
   - Tag: `v1.0.1` (recommended `v` prefix)
   - Title: `v1.0.1` or a short changelog title
   - Description: what changed
4. **Publish** the release — the [Release workflow](.github/workflows/release.yml) will:
   - Set `manifest.json` `version` from the tag (strips leading `v`)
   - Build `custom_components/msnswitch.zip`
   - Attach the zip to the release

### Using GitHub CLI

```bash
cd d:/Projects/hacs-msnswitch

# After updating manifest.json and committing:
gh release create v1.0.1 --title "v1.0.1" --notes "Short changelog here."
```

### Using the GitHub web UI

1. Repository → **Releases** → **Draft a new release**
2. Choose tag `v1.0.1` → create new tag on `main`
3. Publish release

## How HACS picks versions

| Setup | HACS behavior |
|-------|----------------|
| `zip_release: true` in `hacs.json` | Downloads `msnswitch.zip` from the selected release |
| No releases published | Uses files from default branch (`main`) |
| Releases published | User can pick latest releases or `main` in HACS |

## Validation

Every push/PR to `main` runs [HACS validation](.github/workflows/validate.yml).
