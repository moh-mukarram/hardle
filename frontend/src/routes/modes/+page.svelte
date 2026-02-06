<script lang="ts">
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";
    import { logout } from "$lib/utils/api";
    import { getAuthStore } from "$lib/state/auth.svelte";
    import { MODES } from "$lib/config/modes";

    const auth = getAuthStore();

    onMount(() => {
        if (!auth.isAuthenticated && !auth.isLoading) {
            goto("/");
        }
    });

    async function handleLogout() {
        try {
            await logout();
        } catch (e) {
            console.error("Logout failed", e);
        } finally {
            auth.setUser(null);
            goto("/");
        }
    }

    function selectMode(modeId: string) {
        goto(`/game?mode=${modeId}`);
    }
</script>

<div
    class="min-h-screen bg-[#121213] text-white flex flex-col items-center justify-center p-4 font-sans relative"
>
    <!-- Sign Out (Top Right) -->
    <button
        onclick={handleLogout}
        class="absolute top-6 right-6 px-4 py-2 text-sm text-gray-400 hover:text-white border border-gray-700 hover:border-gray-500 rounded-lg transition-colors"
    >
        Sign Out
    </button>

    <!-- Header -->
    <div class="text-center space-y-3 mb-12">
        <h1 class="text-4xl md:text-5xl font-bold tracking-tight">
            Choose Your Challenge
        </h1>
        <p class="text-gray-400 text-lg">
            Not all minds survive the same difficulty.
        </p>
    </div>

    <!-- Cards Grid -->
    <div class="w-full max-w-md space-y-4">
        {#each MODES as mode}
            <button
                onclick={() => selectMode(mode.id)}
                class="w-full group relative flex flex-col items-start p-5 rounded-xl border transition-all duration-300 hover:-translate-y-1 hover:shadow-lg {mode.bg} text-left"
            >
                <div class="flex items-center justify-between w-full mb-1">
                    <span
                        class="px-2 py-0.5 text-[10px] font-bold tracking-wider rounded uppercase {mode.tagColor}"
                    >
                        {mode.tag}
                    </span>
                    <span class="text-sm tracking-widest">{mode.fire}</span>
                </div>
                <h2 class="text-2xl font-bold {mode.color} mb-1">
                    {mode.title}
                </h2>
                <p class="text-sm text-gray-400">{mode.desc}</p>
                {#if mode.footer}
                    <div
                        class="mt-3 w-full text-right text-xs font-mono tracking-widest text-gray-500"
                    >
                        {mode.footer}
                    </div>
                {/if}
            </button>
        {/each}
    </div>

    <!-- Footer removed (Reset text moved to card) -->
</div>
