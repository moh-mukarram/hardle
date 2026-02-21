<script lang="ts">
    import { ChevronDown, ChevronUp } from "lucide-svelte";

    let notes = $state("");
    let greensInput = $state("");
    let yellowsInput = $state("");
    let isCollapsed = $state(true);

    function handleInput(e: Event, setter: (val: string) => void) {
        const input = e.target as HTMLInputElement;
        // Only allow letters, uppercase
        const filtered = input.value.replace(/[^a-zA-Z]/g, "").toUpperCase();
        setter(filtered);
        input.value = filtered; // Force update input display if needed
    }
</script>

<div
    class="w-full lg:max-w-[240px] bg-slate-900/30 backdrop-blur-sm border-l border-cyan-900/40 rounded-lg lg:rounded-l-none lg:rounded-r-lg flex flex-col h-fit transition-all duration-200"
>
    <!-- Header (Clickable on Mobile) -->
    <button
        class="w-full text-center py-4 lg:py-6 border-b border-cyan-900/40 flex items-center justify-center gap-2 cursor-pointer lg:cursor-default"
        onclick={() => (isCollapsed = !isCollapsed)}
        aria-expanded={!isCollapsed}
    >
        <h2 class="text-text-muted text-xs font-bold tracking-[1px] uppercase">
            Rough Work
        </h2>
        <!-- Mobile Toggle Icon -->
        <div class="lg:hidden text-text-muted">
            {#if isCollapsed}
                <ChevronDown size={14} />
            {:else}
                <ChevronUp size={14} />
            {/if}
        </div>
    </button>

    <!-- Content Area (Hidden on mobile if collapsed, always shown on desktop) -->
    <div class="p-6 relative {isCollapsed ? 'hidden lg:block' : 'block'}">
        <!-- Pre-filled prompts - VISUAL FIX: Removed border-b and flex-1 to prevent line bleeding -->
        <div class="font-mono text-sm space-y-3 mb-8">
            <div class="flex items-center gap-2">
                <span class="text-green-400 font-bold whitespace-nowrap"
                    >Greens =</span
                >
                <input
                    type="text"
                    bind:value={greensInput}
                    oninput={(e) => handleInput(e, (v) => (greensInput = v))}
                    class="w-24 bg-transparent text-green-300 font-bold focus:outline-none focus:ring-1 focus:ring-green-500/50 rounded px-1 uppercase transition-shadow"
                    placeholder="---"
                />
            </div>
            <div class="flex items-center gap-2">
                <span class="text-amber-400 font-bold whitespace-nowrap"
                    >Yellows =</span
                >
                <input
                    type="text"
                    bind:value={yellowsInput}
                    oninput={(e) => handleInput(e, (v) => (yellowsInput = v))}
                    class="w-24 bg-transparent text-amber-300 font-bold focus:outline-none focus:ring-1 focus:ring-amber-500/50 rounded px-1 uppercase transition-shadow"
                    placeholder="---"
                />
            </div>
        </div>

        <!-- Free-form writing area -->
        <div class="mt-4">
            <textarea
                bind:value={notes}
                placeholder="Type your deductions here..."
                class="w-full h-[320px] bg-transparent text-cyan-300 font-mono text-sm resize-none outline-none placeholder:text-cyan-900/60 focus:ring-1 focus:ring-cyan-900/60 rounded p-1 transition-shadow"
                style="caret-color: var(--accent-cyan);"
            ></textarea>
        </div>
    </div>
</div>
