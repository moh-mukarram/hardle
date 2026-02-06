<script lang="ts">
    import { signup, login } from "$lib/utils/api";
    import { getAuthStore } from "$lib/state/auth.svelte";
    import { goto } from "$app/navigation";

    let isLogin = $state(true); // Toggle between Login and Signup
    let username = $state("");
    let email = $state("");
    let password = $state("");
    let errorMsg = $state("");
    let loading = $state(false);

    const auth = getAuthStore();

    async function handleSubmit(e: Event) {
        e.preventDefault();
        loading = true;
        errorMsg = "";

        try {
            if (isLogin) {
                const user = await login(email, password);
                auth.setUser(user);
            } else {
                const user = await signup(username, email, password);
                auth.setUser(user);
            }
            goto("/game");
        } catch (err: any) {
            errorMsg = err.message;
        } finally {
            loading = false;
        }
    }
</script>

<div class="flex flex-col justify-center space-y-8 w-full max-w-md">
    <!-- Title -->
    <div class="space-y-2">
        <h1 class="text-5xl font-bold tracking-tight text-white">HARDLE</h1>
        <p class="text-gray-500">Server-Authoritative Word Deduction Game</p>
    </div>

    <div class="space-y-6">
        <h2 class="text-2xl font-semibold text-white">
            {isLogin ? "Log In" : "Create Account"}
        </h2>

        <form onsubmit={handleSubmit} class="space-y-4">
            {#if !isLogin}
                <div class="space-y-2">
                    <label for="username" class="block text-sm text-gray-400"
                        >Username</label
                    >
                    <input
                        id="username"
                        type="text"
                        placeholder="Username"
                        bind:value={username}
                        required
                        class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all"
                    />
                </div>
            {/if}

            <div class="space-y-2">
                <label for="email" class="block text-sm text-gray-400"
                    >Email</label
                >
                <input
                    id="email"
                    type="email"
                    placeholder="Email"
                    bind:value={email}
                    required
                    class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all"
                />
            </div>

            <div class="space-y-2">
                <label for="password" class="block text-sm text-gray-400"
                    >Password</label
                >
                <input
                    id="password"
                    type="password"
                    placeholder="Password"
                    bind:value={password}
                    required
                    class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all"
                />
            </div>

            {#if errorMsg}
                <p class="text-red-500 text-sm">{errorMsg}</p>
            {/if}

            <button
                type="submit"
                disabled={loading}
                class="w-full px-6 py-3 bg-[#d4a933] hover:bg-[#e0b840] text-black font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50"
            >
                {loading ? "Processing..." : isLogin ? "Log In" : "Sign Up"}
            </button>
        </form>

        <p class="text-sm text-gray-500 text-center">
            {isLogin ? "Don't have an account?" : "Already have an account?"}
            <button
                onclick={() => {
                    isLogin = !isLogin;
                    errorMsg = "";
                }}
                class="text-[#d4a933] hover:text-[#e0b840] transition-colors ml-1 underline"
            >
                {isLogin ? "Sign up here" : "Log in here"}
            </button>
        </p>
    </div>
</div>
