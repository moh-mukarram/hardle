<script lang="ts">
    interface Guess {
        letters: string[];
        states: ("correct" | "present" | "absent" | "empty" | "current")[];
        colors?: number[];
    }

    interface Props {
        guesses: Guess[];
        currentRow: number;
        resolvingTileIndex: number;
        gameStatus: "playing" | "won" | "lost";
    }

    let { guesses, currentRow, resolvingTileIndex, gameStatus }: Props =
        $props();

    function getTileStyle(state: string, isResolving: boolean) {
        const baseStyle =
            "w-12 h-12 md:w-14 md:h-14 border-2 flex items-center justify-center text-xl md:text-2xl font-bold transition-all duration-200";

        if (isResolving) {
            return `${baseStyle} border-cyan-400 bg-slate-800 shadow-[0_0_8px_rgba(6,182,212,0.4)] scale-105`;
        }

        switch (state) {
            case "correct":
                return `${baseStyle} bg-green-900/60 border-green-600 text-green-100 shadow-[0_0_6px_rgba(34,197,94,0.3)]`;
            case "present":
                return `${baseStyle} bg-amber-900/60 border-amber-600 text-amber-100 shadow-[0_0_6px_rgba(251,191,36,0.3)]`;
            case "absent":
                return `${baseStyle} bg-slate-800/40 border-slate-700 text-slate-500`;
            case "current":
                return `${baseStyle} border-cyan-500 text-cyan-300 bg-slate-900/40 animate-[borderPulse_80ms_ease-out]`;
            default:
                return `${baseStyle} border-cyan-900/40 text-cyan-300 bg-slate-900/20`;
        }
    }
</script>

<div class="grid grid-rows-6 gap-2 md:gap-2.5">
    {#each guesses as guess, rowIndex}
        <div class="flex gap-2 md:gap-2.5">
            {#each guess.letters as letter, colIndex}
                {@const isResolving =
                    rowIndex === currentRow && colIndex === resolvingTileIndex}
                {@const state = guess.states[colIndex]}
                <div
                    class={getTileStyle(state, isResolving)}
                    style:animation={state === "current" && letter
                        ? "letterFadeIn 150ms ease-out"
                        : undefined}
                >
                    <span
                        style:opacity={letter ? 1 : 0}
                        style:transition="opacity 150ms ease-out"
                    >
                        {letter}
                    </span>
                </div>
            {/each}
        </div>
    {/each}
</div>
