import type { RenderContext } from "../../types.js";
import { isLimitReached } from "../../types.js";
import { getProviderLabel } from "../../stdin.js";
import { critical, label, getQuotaColor, quotaBar, RESET } from "../colors.js";
import { getAdaptiveBarWidth } from "../../utils/terminal.js";
import { t } from "../../i18n/index.js";

export function renderUsageLine(ctx: RenderContext): string | null {
  const display = ctx.config?.display;
  const colors = ctx.config?.colors;

  if (display?.showUsage === false) {
    return null;
  }

  if (!ctx.usageData) {
    return null;
  }

  if (getProviderLabel(ctx.stdin)) {
    return null;
  }

  const usageLabel = label(t("label.usage"), colors);

  if (isLimitReached(ctx.usageData)) {
    const resetTime =
      ctx.usageData.fiveHour === 100
        ? formatResetTime(ctx.usageData.fiveHourResetAt)
        : formatResetTime(ctx.usageData.sevenDayResetAt);
    return `${usageLabel} ${critical(`⚠ ${t("status.limitReached")}${resetTime ? ` (${t("format.resets")} ${resetTime})` : ""}`, colors)}`;
  }

  const threshold = display?.usageThreshold ?? 0;
  const fiveHour = ctx.usageData.fiveHour;
  const sevenDay = ctx.usageData.sevenDay;

  const effectiveUsage = Math.max(fiveHour ?? 0, sevenDay ?? 0);
  if (effectiveUsage < threshold) {
    return null;
  }

  const usageBarEnabled = display?.usageBarEnabled ?? true;
  const sevenDayThreshold = display?.sevenDayThreshold ?? 80;
  const barWidth = getAdaptiveBarWidth();

  // PATCHED: Compact labels — Sesh. ████ 9% (1.2h) | Week. ████ 17% (4.7d)
  const seshLabel = label("Sesh.", colors);
  const weekLabel = label("Week.", colors);

  if (fiveHour === null && sevenDay !== null) {
    const weekPart = formatWindowPart(sevenDay, ctx.usageData.sevenDayResetAt, 7 * 24, barWidth, colors, usageBarEnabled);
    return `${weekLabel} ${weekPart}`;
  }

  const seshPart = formatWindowPart(fiveHour, ctx.usageData.fiveHourResetAt, 5, barWidth, colors, usageBarEnabled);

  if (sevenDay !== null && sevenDay >= sevenDayThreshold) {
    const weekPart = formatWindowPart(sevenDay, ctx.usageData.sevenDayResetAt, 7 * 24, barWidth, colors, usageBarEnabled);
    return `${seshLabel} ${seshPart} | ${weekLabel} ${weekPart}`;
  }

  return `${seshLabel} ${seshPart}`;
}

function formatUsagePercent(
  percent: number | null,
  colors?: RenderContext["config"]["colors"],
): string {
  if (percent === null) {
    return label("--", colors);
  }
  const color = getQuotaColor(percent, colors);
  return `${color}${percent}%${RESET}`;
}

// PATCHED: Window formatter with pace — ████ 30% (2.5h, 50%)
// windowHours = total window size in hours (5 for session, 168 for weekly)
// Pace % = how much of the window's time has elapsed = what % you SHOULD be at
function formatWindowPart(
  percent: number | null,
  resetAt: Date | null,
  windowHours: number,
  barWidth: number,
  colors?: RenderContext["config"]["colors"],
  usageBarEnabled: boolean = true,
): string {
  const pctDisplay = formatUsagePercent(percent, colors);
  const reset = formatResetTime(resetAt);

  // Calculate pace: % of window time elapsed, colored by how fast you're burning
  // Green = under pace (headroom), Amber = on pace, Red = over pace (burning fast)
  let paceDisplay = '';
  if (resetAt && percent !== null) {
    const now = new Date();
    const remainingMs = Math.max(0, resetAt.getTime() - now.getTime());
    const windowMs = windowHours * 3600000;
    const elapsedMs = windowMs - remainingMs;
    const pacePercent = Math.round((elapsedMs / windowMs) * 100);
    if (pacePercent >= 0 && pacePercent <= 100) {
      // Compare actual usage vs expected pace
      const diff = percent - pacePercent; // positive = over-pacing
      const GREEN_ANSI = '\x1b[38;5;85m';   // MINT
      const AMBER_ANSI = '\x1b[38;5;215m';  // WARM_AMBER
      const RED_ANSI = '\x1b[38;5;203m';     // CORAL
      const paceColor = diff > 15 ? RED_ANSI : diff > 0 ? AMBER_ANSI : GREEN_ANSI;
      paceDisplay = `, ${paceColor}${pacePercent}%${RESET}`;
    }
  }

  const time = reset ? ` (${reset}${paceDisplay})` : '';

  if (usageBarEnabled) {
    return `${quotaBar(percent ?? 0, barWidth, colors)} ${pctDisplay}${time}`;
  }
  return `${pctDisplay}${time}`;
}

// PATCHED: Compact reset time — "1.2h", "2.3d", "45m" (no verbose "resets in")
function formatResetTime(resetAt: Date | null): string {
  if (!resetAt) return "";
  const now = new Date();
  const diffMs = resetAt.getTime() - now.getTime();
  if (diffMs <= 0) return "";

  const hours = diffMs / 3600000;
  if (hours < 1) return `${Math.ceil(diffMs / 60000)}m`;
  if (hours < 24) return `${hours.toFixed(1)}h`;
  const days = hours / 24;
  return `${days.toFixed(1)}d`;
}
