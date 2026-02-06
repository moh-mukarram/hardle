<script lang="ts">
    import { Eye, EyeOff } from "lucide-svelte";

    interface RowCounts {
        greenCount: number;
        yellowCount: number;
    }

    interface Props {
        rows: RowCounts[];
        showGreen: boolean;
        showYellow: boolean;
        onToggleGreen: () => void;
        onToggleYellow: () => void;
    }

    let { rows, showGreen, showYellow, onToggleGreen, onToggleYellow } =
        $props<Props>();
</script>

<div class="flex flex-col gap-3">
    <!-- Toggles -->
    <div class="flex gap-2">
        <button
            onclick={onToggleGreen}
            class={`flex-1 px-4 py-2.5 text-sm font-bold rounded flex items-center justify-center gap-2 transition-colors ${
                !showGreen
                    ? "bg-[#3a3a3c] text-gray-500"
                    : "bg-[#6aaa64] text-white hover:bg-[#5a9954]"
            }`}
        >
            {#if !showGreen}<EyeOff size={16} />{:else}<Eye size={16} />{/if}
            <span class="hidden sm:inline">Green</span>
        </button>
        <button
            onclick={onToggleYellow}
            class={`flex-1 px-4 py-2.5 text-sm font-bold rounded flex items-center justify-center gap-2 transition-colors ${
                !showYellow
                    ? "bg-[#3a3a3c] text-gray-500"
                    : "bg-[#c9b458] text-white hover:bg-[#b9a448]"
            }`}
        >
            {#if !showYellow}<EyeOff size={16} />{:else}<Eye size={16} />{/if}
            <span class="hidden sm:inline">Yellow</span>
        </button>
    </div>

    <!-- Rows -->
    <div class="flex flex-col gap-1.5">
        {#each rows as row, i}
            <div class="flex gap-1.5 items-center">
                <!-- Row number -->
                <div class="w-6 text-xs text-gray-600 font-bold text-right">
                    {i + 1}
                </div>

                <!-- Green -->
                {#if showGreen}
                    <div
                        class="w-14 h-14 sm:w-16 sm:h-16 border-2 border-[#6aaa64] bg-[#121213] flex items-center justify-center"
                    >
                        <span
                            class="text-2xl sm:text-3xl font-bold text-[#6aaa64]"
                            >{row.greenCount}</span
                        >
                    </div>
                {/if}

                <!-- Yellow -->
                {#if showYellow}
                    <div
                        class="w-14 h-14 sm:w-16 sm:h-16 border-2 border-[#c9b458] bg-[#121213] flex items-center justify-center"
                    >
                        <span
                            class="text-2xl sm:text-3xl font-bold text-[#c9b458]"
                            >{row.yellowCount}</span
                        >
                    </div>
                {/if}
            </div>
        {/each}
    </div>
</div>
