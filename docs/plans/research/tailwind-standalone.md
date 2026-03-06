# Tailwind CSS v4 Standalone CLI -- Research for Django (No Node.js)

**Date:** 2026-03-06
**Tailwind Version:** v4.x (latest release as of writing: v4.2.1)

---

## 1. Downloading and Installing the Standalone CLI Binary

The Tailwind v4 standalone CLI is a self-contained executable bundled with Bun. It includes all
dependencies (Lightning CSS for minification, Parcel Watcher for file monitoring) and first-party
plugins (`@tailwindcss/forms`, `@tailwindcss/typography`, `@tailwindcss/aspect-ratio`). No Node.js
or npm required.

### Download URL Pattern

```
# Latest release (follows redirects to current version)
https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-{PLATFORM}-{ARCH}

# Pinned version
https://github.com/tailwindlabs/tailwindcss/releases/download/v{VERSION}/tailwindcss-{PLATFORM}-{ARCH}
```

### Available Binary Names

| Platform       | Binary Name                    | Notes                        |
|----------------|--------------------------------|------------------------------|
| macOS ARM64    | `tailwindcss-macos-arm64`      | Apple Silicon (M1/M2/M3/M4) |
| macOS x64      | `tailwindcss-macos-x64`        | Intel Macs                   |
| Linux x64      | `tailwindcss-linux-x64`        | glibc-based (Debian/Ubuntu)  |
| Linux ARM64    | `tailwindcss-linux-arm64`      | glibc-based                  |
| Linux x64 musl | `tailwindcss-linux-x64-musl`   | Alpine Linux                 |
| Linux ARM64 musl | `tailwindcss-linux-arm64-musl` | Alpine Linux ARM             |
| Windows x64    | `tailwindcss-windows-x64.exe`  |                              |

### Installation (macOS example)

```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-macos-arm64
chmod +x tailwindcss-macos-arm64
mv tailwindcss-macos-arm64 /usr/local/bin/tailwindcss
```

### Installation (Linux x64 example)

```bash
curl -sLO https://github.com/tailwindlabs/tailwindcss/releases/latest/download/tailwindcss-linux-x64
chmod +x tailwindcss-linux-x64
mv tailwindcss-linux-x64 /usr/local/bin/tailwindcss
```

### Python Wrapper (pytailwindcss)

There is a `pytailwindcss` package on PyPI that wraps the standalone binary. However, it has
uncertain v4 support and adds an unnecessary abstraction layer. For a Django project, downloading
the binary directly is more transparent and reliable.

### Django Integration Library (django-tailwind-cli)

The `django-tailwind-cli` package (from django-commons) automates binary management for Django:

```python
# settings.py
INSTALLED_APPS = ["django_tailwind_cli", ...]
TAILWIND_CLI_VERSION = "4.1.3"          # Pin version
TAILWIND_CLI_AUTOMATIC_DOWNLOAD = True  # Auto-downloads binary
TAILWIND_CLI_SRC_CSS = "src/styles.css"
TAILWIND_CLI_DIST_CSS = "css/tailwind.css"
```

Commands: `python manage.py tailwind build`, `tailwind watch`, `tailwind runserver`.

For our starter-django skill, using the raw binary directly (not the Django library) gives full
control and avoids a dependency. The library is worth knowing about but we should control the
build ourselves.

---

## 2. Building CSS from an input.css File

### The input.css File (v4 format)

Tailwind v4 uses `@import "tailwindcss"` instead of the old v3 `@tailwind base/components/utilities`
directives:

```css
@import "tailwindcss";
```

That single line is all that is required for a basic setup. Tailwind v4 does NOT require a
`tailwind.config.js` file -- there is no `init` command in v4.

### Build Command

```bash
# Basic build
tailwindcss -i src/input.css -o static/css/tailwind.css

# Minified production build
tailwindcss -i src/input.css -o static/css/tailwind.css --minify
```

Flags:
- `-i` / `--input` -- Input CSS file path
- `-o` / `--output` -- Output CSS file path
- `--minify` -- Minify output (uses Lightning CSS internally)
- `--cwd <path>` -- Change working directory for template scanning
- `--map` -- Generate inline source map
- `--map <file>` -- Generate external source map file

---

## 3. Watch Mode for Development

```bash
tailwindcss -i src/input.css -o static/css/tailwind.css --watch
```

Watch mode uses `@parcel/watcher` internally for file system subscriptions. It features:

- **Incremental scanning** -- Only scans changed files for new class candidates
- **Skip unchanged** -- If no new candidates found, the build is skipped entirely
- **Debouncing** -- Batches rapid file changes
- **Persistent mode** -- `--watch=always` keeps watching even when stdin closes

For Django development, run the watcher in a separate terminal or as a background process
alongside `manage.py runserver`.

---

## 4. Docker Multi-Stage Build

### Recommended Approach: Download binary, build CSS in a stage

```dockerfile
# ============================================================
# Stage 1: Build Tailwind CSS
# ============================================================
FROM debian:bookworm-slim AS tailwind-build

ARG TAILWIND_VERSION=4.1.3
ARG TARGETARCH

# Download the correct binary for the build platform
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates \
    && ARCH=$(case ${TARGETARCH} in \
         amd64) echo "x64" ;; \
         arm64) echo "arm64" ;; \
         *) echo "x64" ;; \
       esac) \
    && curl -sL -o /usr/local/bin/tailwindcss \
       "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-${ARCH}" \
    && chmod +x /usr/local/bin/tailwindcss

WORKDIR /build
# Copy only files needed for Tailwind scanning
COPY frontend/src/input.css ./frontend/src/input.css
COPY frontend/src/ ./frontend/src/
COPY templates/ ./templates/

# Build production CSS
RUN tailwindcss -i frontend/src/input.css -o /build/static/css/tailwind.css --minify


# ============================================================
# Stage 2: Python / Django
# ============================================================
FROM python:3.12-slim-bookworm AS final

# ... Python deps, Django setup, etc. ...

# Copy the pre-built CSS from the tailwind stage
COPY --from=tailwind-build /build/static/css/tailwind.css /app/static/css/tailwind.css
```

### Alpine-Based Docker Image (Caution)

If using Alpine Linux (`python:3.12-alpine`), use the musl binary variant:

```dockerfile
# Use the musl variant for Alpine
RUN curl -sL -o /usr/local/bin/tailwindcss \
    "https://github.com/tailwindlabs/tailwindcss/releases/download/v${TAILWIND_VERSION}/tailwindcss-linux-x64-musl" \
    && chmod +x /usr/local/bin/tailwindcss
```

**Known issue:** The v4 musl binaries (especially ARM64) may not be fully statically linked.
If `tailwindcss: not found` errors occur on Alpine despite the binary being present, install
`build-base` as a workaround:

```dockerfile
RUN apk add --no-cache build-base
```

Using `debian:bookworm-slim` or `python:3.12-slim-bookworm` avoids this issue entirely and is
the recommended approach.

### Alternative: Build CSS Locally and COPY

For simpler setups, build CSS during CI/CD before the Docker build and just COPY the artifact:

```dockerfile
COPY static/css/tailwind.css /app/static/css/tailwind.css
```

This removes the Tailwind binary from the Docker image entirely, at the cost of requiring the
binary in CI.

---

## 5. The input.css File Format for Tailwind v4

### Minimal

```css
@import "tailwindcss";
```

### With Source Path Override

When the CSS file is not in the project root, tell Tailwind where to scan:

```css
@import "tailwindcss" source("../");
```

The `source()` function on the import sets the base directory for automatic content detection.
Paths are relative to the CSS file.

### With Custom Theme

```css
@import "tailwindcss";

@theme {
  --color-brand-50: oklch(0.97 0.02 250);
  --color-brand-500: oklch(0.55 0.20 250);
  --color-brand-900: oklch(0.25 0.10 250);
  --font-display: "Inter", sans-serif;
  --breakpoint-3xl: 120rem;
}
```

### With Explicit Source Directories

```css
@import "tailwindcss";
@source "../templates";
@source "../frontend/src";
```

### With Safelisted Classes

```css
@import "tailwindcss";
@source inline("underline");
@source inline("{hover:,focus:,}bg-brand-{500,600,700}");
```

### Disabling Automatic Detection (Explicit Only)

```css
@import "tailwindcss" source(none);
@source "../templates";
@source "../frontend/src/components";
```

### With First-Party Plugins (Bundled in Standalone)

```css
@import "tailwindcss";
@plugin "@tailwindcss/typography";
@plugin "@tailwindcss/forms";
```

### With Legacy JS Config (if needed)

```css
@config "./tailwind.config.js";
@import "tailwindcss";
```

### Custom Utilities

```css
@import "tailwindcss";

@utility content-auto {
  content-visibility: auto;
}
```

### Full Django-Oriented Example

```css
@import "tailwindcss" source("../");

@theme {
  --color-primary-50: oklch(0.97 0.02 250);
  --color-primary-100: oklch(0.94 0.04 250);
  --color-primary-500: oklch(0.55 0.20 250);
  --color-primary-600: oklch(0.48 0.20 250);
  --color-primary-700: oklch(0.40 0.18 250);
  --color-primary-900: oklch(0.25 0.10 250);
}
```

---

## 6. How the Standalone CLI Scans Template Files

### Automatic Content Detection

Tailwind v4 automatically discovers all template files in your project. It does NOT require
a `content` array in a config file (unlike v3). The scanner:

1. Starts from the CSS file's directory (or the directory set via `source()` / `--cwd`)
2. Recursively scans all files
3. **Skips** files matching `.gitignore` patterns (only in git repos)
4. **Skips** `node_modules/` directories
5. **Skips** binary files (images, videos, archives, etc.)
6. **Skips** CSS files
7. **Skips** package manager lock files

### How Class Detection Works

The scanner (powered by `@tailwindcss/oxide`, written in Rust) treats files as plain text.
It does NOT parse HTML/JS/Python semantically. Instead, it:

1. Tokenizes files looking for strings matching class name patterns
2. Matches tokens against known Tailwind utilities
3. Generates CSS only for matched utilities

This means it works with **any** template language -- Django templates, Jinja2, HTML, JSX, Vue,
Python files containing class strings, etc. No special configuration needed for `.html` or `.py`
files.

### Controlling What Gets Scanned

| Directive                              | Purpose                                          |
|----------------------------------------|--------------------------------------------------|
| `source("../path")` on `@import`      | Set the base scan directory                      |
| `source(none)` on `@import`           | Disable automatic scanning entirely              |
| `@source "../path"`                    | Add an explicit directory to scan                |
| `@source not "../path"`               | Exclude a directory from scanning                |
| `@source inline("classes")`           | Force-generate specific utilities (safelist)     |
| `@source not inline("classes")`       | Prevent specific utilities from being generated  |
| `--cwd <path>` CLI flag               | Override the working directory for scanning      |

### Django-Specific Scanning Considerations

For a typical Django project structure:

```
project/
  manage.py
  myapp/
    templates/        <-- HTML templates with Tailwind classes
      base.html
      index.html
    views.py          <-- May contain class strings for dynamic rendering
  frontend/
    src/
      input.css       <-- Tailwind entry point
      components/     <-- React/JS components with Tailwind classes
  static/
    css/
      tailwind.css    <-- Generated output
```

The input.css should use `source("../../")` (relative to the CSS file) to scan from the project
root, or use explicit `@source` directives:

```css
@import "tailwindcss" source("../../");
```

Or equivalently:

```css
@import "tailwindcss" source(none);
@source "../../myapp/templates";
@source "../components";
```

### Dynamic Class Names (Critical Caveat)

Tailwind cannot detect dynamically constructed class names. This applies to Django templates too:

```html
<!-- WILL NOT WORK -- Tailwind cannot see "text-red-600" or "text-green-600" -->
<p class="text-{{ color }}-600">Hello</p>

<!-- WORKS -- Full class names are visible as plain text -->
{% if error %}
  <p class="text-red-600">Error</p>
{% else %}
  <p class="text-green-600">Success</p>
{% endif %}
```

---

## 7. Key Differences: v4 Standalone vs v3 Standalone

| Aspect                  | v3                                      | v4                                        |
|-------------------------|-----------------------------------------|-------------------------------------------|
| Init command            | `tailwindcss init`                      | None (not needed)                         |
| Config file             | `tailwind.config.js` required           | Optional, config lives in CSS             |
| Input CSS               | `@tailwind base/components/utilities`   | `@import "tailwindcss"`                   |
| Content paths           | `content: [...]` in config              | Automatic detection + `@source`           |
| Theme customization     | JS config `theme.extend`                | `@theme { }` in CSS                       |
| Plugins                 | `plugins: [...]` in config              | `@plugin "..."` in CSS                    |
| Custom utilities        | JS plugin API                           | `@utility name { }` in CSS               |
| Engine                  | PostCSS-based                           | Lightning CSS + Oxide (Rust)              |
| Bundled plugins         | `forms`, `typography`, `aspect-ratio`   | Same, bundled in standalone               |

---

## 8. Summary: Recommended Approach for starter-django

1. **Download** the standalone binary in Docker (multi-stage) or CI
2. **Create** `frontend/src/input.css` with `@import "tailwindcss" source("../../");`
3. **Build** with `tailwindcss -i frontend/src/input.css -o static/css/tailwind.css --minify`
4. **Watch** during dev with `--watch` flag alongside `manage.py runserver`
5. **No Node.js** anywhere in the pipeline
6. Use `debian:bookworm-slim` base images to avoid Alpine musl issues
7. Pin `TAILWIND_VERSION` as a build arg for reproducibility

---

## Sources

- [Tailwind CLI Installation (Official Docs)](https://tailwindcss.com/docs/installation/tailwind-cli)
- [Standalone CLI Blog Post](https://tailwindcss.com/blog/standalone-cli)
- [Detecting Classes in Source Files (Official Docs)](https://tailwindcss.com/docs/detecting-classes-in-source-files)
- [Functions and Directives (Official Docs)](https://tailwindcss.com/docs/functions-and-directives)
- [Tailwind CSS v4.0 Release](https://tailwindcss.com/blog/tailwindcss-v4)
- [Beginner Tutorial for Standalone CLI v4 (GitHub Discussion)](https://github.com/tailwindlabs/tailwindcss/discussions/15855)
- [Tailwind Standalone CLI in Docker (GitHub Discussion)](https://github.com/tailwindlabs/tailwindcss/discussions/8027)
- [v4 Standalone Binary Static Builds Issue (GitHub Discussion)](https://github.com/tailwindlabs/tailwindcss/discussions/17204)
- [CLI and Standalone Technical Analysis (DeepWiki)](https://deepwiki.com/tailwindlabs/tailwindcss/4.3-cli-and-standalone)
- [django-tailwind-cli (GitHub)](https://github.com/django-commons/django-tailwind-cli)
- [django-tailwind-cli (ReadTheDocs)](https://django-tailwind-cli.readthedocs.io/latest/)
- [Build Tailwind v4 Locally with Docker](https://arashtaher.com/blog/build-tailwind-v4-locally-with-docker/)
- [Tailwind v4 WordPress Standalone CLI Guide](https://librevious.com/tailwind-css-v4-in-a-wordpress-plugin-the-standalone-cli-guide/)
- [Guide to @source Directive (Tailkits)](https://tailkits.com/blog/tailwind-at-source-directive/)
- [GitHub Releases Page](https://github.com/tailwindlabs/tailwindcss/releases)
