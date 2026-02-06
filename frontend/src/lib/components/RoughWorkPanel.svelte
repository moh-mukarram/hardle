<script lang="ts">
    let notes = $state("");
    let greensInput = $state("");
    let yellowsInput = $state("");

    function handleInput(e: Event, setter: (val: string) => void) {
        const input = e.target as HTMLInputElement;
        // Only allow letters, uppercase
        const filtered = input.value.replace(/[^a-zA-Z]/g, "").toUpperCase();
        setter(filtered);
        input.value = filtered; // Force update input display if needed
    }
</script>

<div
    class="w-full max-w-[240px] bg-[#1e1e1e] border-l border-[#333333] rounded-tr-lg rounded-br-lg flex flex-col h-fit"
>
    <!-- Header -->
    <div class="text-center py-6 border-b border-[#333333]">
        <h2 class="text-[#aaaaaa] text-xs font-bold tracking-[1px] uppercase">
            Rough Work
        </h2>
    </div>

    <!-- Content Area -->
    <div class="p-6 relative">
        <!-- Pre-filled prompts - VISUAL FIX: Removed border-b and flex-1 to prevent line bleeding -->
        <div class="font-mono text-sm space-y-3 mb-8">
            <div class="flex items-center gap-2">
                <span class="text-[#6aaa64] font-bold whitespace-nowrap"
                    >Greens =</span
                >
                <input
                    type="text"
                    bind:value={greensInput}
                    oninput={(e) => handleInput(e, (v) => (greensInput = v))}
                    class="w-24 bg-transparent text-[#6aaa64] font-bold outline-none px-1 uppercase"
                    placeholder="---"
                />
            </div>
            <div class="flex items-center gap-2">
                <span class="text-[#c9b458] font-bold whitespace-nowrap"
                    >Yellows =</span
                >
                <input
                    type="text"
                    bind:value={yellowsInput}
                    oninput={(e) => handleInput(e, (v) => (yellowsInput = v))}
                    class="w-24 bg-transparent text-[#c9b458] font-bold outline-none px-1 uppercase"
                    placeholder="---"
                />
            </div>
        </div>

        <!-- Ruled lines area - Starting clearly below the inputs -->
        <div class="relative border-t border-white/5 pt-2">
            <!-- Background lines -->
            <div class="absolute inset-0 pointer-events-none select-none">
                {#each Array(10) as _, i}
                    <div
                        class="border-b border-white/10"
                        style="height: 32px;"
                    ></div>
                {/each}
            </div>

            <!-- Textarea -->
            <textarea
                bind:value={notes}
                placeholder="Type your deductions here..."
                class="w-full h-[320px] bg-transparent text-[#d4d4d4] font-mono text-sm resize-none outline-none relative z-10 leading-[32px]"
                style="caret-color: #6aaa64; line-height: 32px;"
            ></textarea>
        </div>
    </div>
</div>
