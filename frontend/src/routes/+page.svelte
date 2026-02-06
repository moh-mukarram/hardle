<script lang="ts">
    import AuthForm from "$lib/components/AuthForm.svelte";
    import Leaderboard from "$lib/components/Leaderboard.svelte";
    import { getMe } from "$lib/utils/api";
    import { getAuthStore } from "$lib/state/auth.svelte";
    import { onMount } from "svelte";
    import { goto } from "$app/navigation";

    const auth = getAuthStore();

    onMount(async () => {
        try {
            const user = await getMe();
            auth.setUser(user);
            if (auth.isAuthenticated) {
                goto("/game");
            }
        } catch {
            auth.setUser(null);
        }
    });
</script>

<div
    class="min-h-screen flex items-center justify-center px-8 py-12 dark bg-[#0a0a0a] text-white"
>
    <!-- Gradient Background -->
    <div
        class="absolute inset-0 bg-gradient-to-br from-[#0a0a0a] via-[#1a1a1a] to-[#0f0f0f] z-0 pointer-events-none"
    ></div>

    <div
        class="relative z-10 w-full max-w-6xl grid grid-cols-1 lg:grid-cols-2 gap-16"
    >
        <!-- Left Column: Auth -->
        <div class="flex flex-col justify-center items-center lg:items-start">
            <AuthForm />
        </div>

        <!-- Right Column: Leaderboard -->
        <div class="flex flex-col justify-center">
            <Leaderboard />
        </div>
    </div>
</div>
