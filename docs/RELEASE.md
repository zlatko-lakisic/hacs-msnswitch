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

**Important:** `filename` in `hacs.json` must include the `.zip` extension (e.g. `"msnswitch.zip"`), matching the release asset name exactly.
| No releases published | Uses files from default branch (`main`) |
| Releases published | User can pick latest releases or `main` in HACS |

## Validation

Every push/PR to `main` runs:

- [HACS validation](.github/workflows/validate.yml)
- [Hassfest](.github/workflows/hassfest.yml)

### GitHub repository settings (HACS checks)

These are **not** in git — set on the GitHub repo (already configured for `zlatko-lakisic/hacs-msnswitch`):

| Check | Requirement |
|-------|-------------|
| Description | Short summary on the repo home page |
| Topics | e.g. `home-assistant`, `homeassistant`, `hacs`, `hacs-integration`, `integration` |
| Issues | Enabled |
| Brand | `custom_components/msnswitch/brand/icon.png` in the repo |

```bash
gh repo edit zlatko-lakisic/hacs-msnswitch \
  --description "Home Assistant HACS integration for Proxicast MSNSwitch UIS-622/722 smart power switches" \
  --add-topic home-assistant --add-topic homeassistant --add-topic hacs \
  --add-topic hacs-integration --add-topic integration --add-topic msnswitch \
  --enable-issues=true
```
