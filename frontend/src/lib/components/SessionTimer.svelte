<script lang="ts">
    interface Props {
        timeRemaining: number;
        sessionTimeLimit: number;
        compact?: boolean;
        gameStatus?: "playing" | "won" | "lost";
    }

    let {
        timeRemaining,
        sessionTimeLimit,
        compact = false,
        gameStatus = "playing",
    }: Props = $props();

    let minutes = $derived(Math.floor(timeRemaining / 60));
    let seconds = $derived(timeRemaining % 60);
    let timeString = $derived(
        `${minutes}:${seconds.toString().padStart(2, "0")}`,
    );

    let isLowTime = $derived(timeRemaining <= 30 && timeRemaining > 0);
    let isExpired = $derived(timeRemaining === 0);
    let isEnded = $derived(gameStatus !== "playing");
</script>

{#if compact}
    <div class="flex items-center justify-center gap-2">
        <span
            class={`text-[9px] tracking-[0.12em] uppercase transition-all duration-300 ${
                isEnded
                    ? "text-cyan-500/50"
                    : isExpired
                      ? "text-red-400/80"
                      : isLowTime
                        ? "text-amber-400/80"
                        : "text-cyan-500/60"
            }`}
        >
            {isEnded
                ? "SESSION ENDED"
                : isExpired
                  ? "SESSION EXPIRED"
                  : "SESSION TIME REMAINING"}
        </span>
        <span
            class={`text-sm font-mono font-bold transition-all duration-300 ${
                isEnded
                    ? "text-cyan-400/60"
                    : isExpired
                      ? "text-red-400"
                      : isLowTime
                        ? "text-amber-400 drop-shadow-[0_0_6px_rgba(251,191,36,0.3)]"
                        : "text-cyan-400"
            }`}
        >
            <span class="transition-opacity duration-200">
                {isExpired ? "EXPIRED" : timeString}
            </span>
        </span>
    </div>
{:else}
    <div class="flex items-center gap-2">
        <span
            class={`text-xs tracking-wider transition-all duration-300 ${
                isExpired
                    ? "text-red-400/80"
                    : isLowTime
                      ? "text-amber-400/80"
                      : "text-cyan-500/80"
            }`}
        >
            {isExpired ? "SESSION EXPIRED" : "SESSION TIME"}
        </span>
        {#if !isExpired}
            <span
                class={`text-sm font-mono font-bold transition-all duration-300 ${
                    isLowTime
                        ? "text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.4)]"
                        : "text-cyan-400"
                }`}
            >
                <span class="transition-opacity duration-200">
                    {timeString}
                </span>
            </span>
        {/if}
    </div>
{/if}
