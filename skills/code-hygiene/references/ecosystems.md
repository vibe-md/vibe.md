# Ecosystem commands

The workflow in `SKILL.md` is the same in every language: installed version first, local source of truth second, documentation for that exact version third, memory last. These are the equivalent commands outside JavaScript and TypeScript.

## Real: find the installed version and inspect an API

| Ecosystem | Installed version | Inspect the API |
| --- | --- | --- |
| Python | `pip show <pkg>` | `python -c "import inspect, <mod>; print(inspect.signature(<mod>.<fn>))"` |
| Go | `go list -m <module>` | `go doc <pkg>.<Symbol>` |
| Rust | `cargo tree -p <crate>` | docs.rs for the exact version in `Cargo.lock` |
| Ruby | `bundle info <gem>` | `bundle exec ri <Class#method>` |
| Swift (SPM) | `Package.resolved` | The package source under `.build/checkouts` |
| Android (Gradle) | `./gradlew dependencies` | The sources jar or documentation for the exact version |

The compiler check is the language's own: `mypy` or `pyright` for typed Python, `go build ./...` and `go vet ./...`, `cargo check`, `swift build`, `./gradlew compileDebugKotlin`.

## Used: find unused code

| Ecosystem | Tool | Notes |
| --- | --- | --- |
| Python | `vulture` | Reports confidence levels; treat low-confidence results as leads only. |
| Go | `staticcheck` (check U1000) | Exported identifiers are not reported. |
| Rust | Compiler `dead_code` warnings from `cargo check` | `pub` items in a library crate are not reported. |
| Ruby | `debride` | Expect false positives from metaprogramming. |
| Swift | `periphery` | Needs a build; respects `@objc` and Interface Builder references. |
| Android (Kotlin/Java) | Android Lint `UnusedResources`, IDE unused-symbol inspection | Resources can be referenced from XML and by name at runtime. |

Every tool here reports false positives. Confirm each candidate by searching the repository for its name, including configuration, resources, and native folders, before proposing its removal.
