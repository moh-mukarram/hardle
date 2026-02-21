<script lang="ts">
    interface RowCounts {
        greenCount: number;
        yellowCount: number;
    }

    interface Props {
        rows: RowCounts[];
    }

    let { rows }: Props = $props();
</script>

<div class="flex flex-col gap-1.5">
    {#each rows as row, i}
        <div class="flex gap-1.5 items-center">
            <!-- Row number -->
            <div class="w-6 text-xs text-text-muted font-bold text-right">
                {i + 1}
            </div>

            <!-- Green -->
            <div
                class="w-14 h-14 sm:w-16 sm:h-16 border-2 border-green-600 bg-green-900/60 shadow-[var(--glow-tile-green)] flex items-center justify-center transition-all duration-200"
            >
                <span class="text-2xl sm:text-3xl font-bold text-green-100">
                    {#if row.greenCount > 0}{row.greenCount}{/if}
                </span>
            </div>

            <!-- Yellow -->
            <div
                class="w-14 h-14 sm:w-16 sm:h-16 border-2 border-amber-600 bg-amber-900/60 shadow-[var(--glow-tile-amber)] flex items-center justify-center transition-all duration-200"
            >
                <span class="text-2xl sm:text-3xl font-bold text-amber-100">
                    {#if row.yellowCount > 0}{row.yellowCount}{/if}
                </span>
            </div>
        </div>
    {/each}
</div>
