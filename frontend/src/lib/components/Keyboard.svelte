<script lang="ts">
    import { Delete } from "lucide-svelte";
    import type { GuessDetail } from "$lib/utils/api";

    interface Props {
        guesses: GuessDetail[];
        onKey: (key: string) => void;
    }

    let { guesses, onKey }: Props = $props();

    const ROWS = [
        ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["ENTER", "Z", "X", "C", "V", "B", "N", "M", "BACKSPACE"],
    ];

    // Compute key colors derived from guesses
    const getKeyColors = (guesses: GuessDetail[]) => {
        const colors: Record<string, number> = {};

        for (const guess of guesses) {
            guess.word.split("").forEach((char, i) => {
                const color = guess.colors[i];
                const existing = colors[char] ?? -1;
                // Upgrade color: Green (2) > Yellow (1) > Gray (0) > None (-1)
                // Note: Gray should overwrite "None", but not Green or Yellow.
                // Yellow should overwrite Gray or None, but not Green.
                // Green overwrites everything.

                if (color === 2) {
                    colors[char] = 2;
                } else if (color === 1) {
                    if (existing !== 2) colors[char] = 1;
                } else if (color === 0) {
                    if (existing === -1) colors[char] = 0;
                }
            });
        }
        return colors;
    };

    let keyColors = $derived(getKeyColors(guesses));

    const getKeyClass = (key: string, color: number) => {
        const base =
            "px-2 py-3 md:px-4 md:py-4 rounded border-2 font-bold text-xs md:text-sm transition-all duration-200 active:scale-95 flex items-center justify-center select-none cursor-pointer";
        const size =
            key.length > 1 ? "min-w-[60px]" : "min-w-[32px] md:min-w-[40px]";

        let bg =
            "bg-slate-900/40 border-cyan-900/60 text-cyan-300 hover:bg-slate-800/60 hover:border-cyan-700"; // Default

        if (color === 2)
            bg =
                "bg-green-900/60 border-green-600 text-green-100 shadow-[var(--glow-key-green)]";
        else if (color === 1)
            bg =
                "bg-amber-900/60 border-amber-600 text-amber-100 shadow-[var(--glow-key-amber)]";
        else if (color === 0)
            bg = "bg-slate-800/40 border-slate-700 text-slate-500"; // Absent

        return `${base} ${size} ${bg}`;
    };
</script>

<div class="w-full max-w-lg flex flex-col gap-2 p-2">
    {#each ROWS as row}
        <div class="flex justify-center gap-1.5">
            {#each row as key}
                <button
                    class={getKeyClass(key, keyColors[key] ?? -1)}
                    onclick={() => onKey(key)}
                >
                    {#if key === "BACKSPACE"}
                        <Delete size={20} />
                    {:else}
                        {key}
                    {/if}
                </button>
            {/each}
        </div>
    {/each}
</div>
