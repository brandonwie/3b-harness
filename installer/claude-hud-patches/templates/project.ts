import type { RenderContext } from "../../types.js";
import { getModelName, getProviderLabel } from "../../stdin.js";
import { cyan, green, magenta, violet, yellow, red, dim } from "../colors.js";

/**
 * Parse version from model ID when display_name lacks it.
 * "claude-opus-4-7" → "Opus 4.7"
 * "claude-haiku-4-5-20251001" → "Haiku 4.5"
 */
function getModelDisplayWithVersion(stdin: {
  model?: { display_name?: string; id?: string };
}): string {
  const displayName = stdin.model?.display_name;
  const modelId = stdin.model?.id;

  // If display_name already has a version number, use it directly
  if (displayName && /\d/.test(displayName)) {
    return displayName;
  }

  // Parse version from model ID: "claude-{family}-{major}-{minor}[...]"
  if (modelId) {
    const match = modelId.match(/^claude-(\w+)-(\d+)-(\d+)/);
    if (match) {
      const name = match[1].charAt(0).toUpperCase() + match[1].slice(1);
      return `${name} ${match[2]}.${match[3]}`;
    }
  }

  return displayName ?? modelId ?? "Unknown";
}

export function renderProjectLine(ctx: RenderContext): string | null {
  const display = ctx.config?.display;
  const parts: string[] = [];

  // Read env vars passed by statusline-wrapper.sh
  const envLabel = process.env.CLAUDE_HUD_ENV_LABEL;
  const envVersion = process.env.CLAUDE_HUD_ENV_VERSION;

  if (display?.showModel !== false) {
    const model = getModelDisplayWithVersion(ctx.stdin);
    const providerLabel = getProviderLabel(ctx.stdin);
    const planName =
      display?.showUsage !== false ? ctx.usageData?.planName : undefined;
    const hasApiKey = !!process.env.ANTHROPIC_API_KEY;
    const billingLabel = hasApiKey ? red("API") : planName;
    const planDisplay = providerLabel ?? billingLabel;
    const modelDisplay = planDisplay ? `${model} | ${planDisplay}` : model;
    parts.push(cyan(`[${modelDisplay}]`));
  }

  if (ctx.stdin.cwd) {
    const segments = ctx.stdin.cwd.split(/[/\\]/).filter(Boolean);
    const pathLevels = ctx.config?.pathLevels ?? 1;
    const projectPath =
      segments.length > 0 ? segments.slice(-pathLevels).join("/") : "/";

    let gitPart = "";
    const gitConfig = ctx.config?.gitStatus;
    const showGit = gitConfig?.enabled ?? true;

    if (showGit && ctx.gitStatus) {
      const gitParts: string[] = [ctx.gitStatus.branch];

      if ((gitConfig?.showDirty ?? true) && ctx.gitStatus.isDirty) {
        gitParts.push("*");
      }

      if (gitConfig?.showAheadBehind) {
        if (ctx.gitStatus.ahead > 0) {
          gitParts.push(` ↑${ctx.gitStatus.ahead}`);
        }
        if (ctx.gitStatus.behind > 0) {
          gitParts.push(` ↓${ctx.gitStatus.behind}`);
        }
      }

      if (gitConfig?.showFileStats && ctx.gitStatus.fileStats) {
        const { modified, added, deleted, untracked } = ctx.gitStatus.fileStats;
        const statParts: string[] = [];
        if (modified > 0) statParts.push(`!${modified}`);
        if (added > 0) statParts.push(`+${added}`);
        if (deleted > 0) statParts.push(`✘${deleted}`);
        if (untracked > 0) statParts.push(`?${untracked}`);
        if (statParts.length > 0) {
          gitParts.push(` ${statParts.join(" ")}`);
        }
      }

      gitPart = ` ${magenta("git:(")}${cyan(gitParts.join(""))}${magenta(")")}`;
    }

    parts.push(`${yellow(projectPath)}${gitPart}`);
  }

  // Session name
  if (display?.showSessionName && ctx.transcript.sessionName) {
    parts.push(dim(ctx.transcript.sessionName));
  }

  // Environment version (from wrapper env var)
  if (envLabel && envVersion) {
    parts.push(`${violet(envLabel)} ${green(envVersion)}`);
  }

  if (parts.length === 0) {
    return null;
  }

  return parts.join(" \u2502 ");
}
