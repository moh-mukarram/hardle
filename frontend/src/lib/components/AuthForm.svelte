<script lang="ts">
    import { signup, login } from "$lib/utils/api";
    import { getAuthStore } from "$lib/state/auth.svelte";
    import { goto } from "$app/navigation";
    import { Eye, EyeOff } from "lucide-svelte";

    let isLogin = $state(true); // Toggle between Login and Signup
    let username = $state("");
    let email = $state("");
    let password = $state("");
    let confirmPassword = $state("");
    let showPassword = $state(false);
    let showConfirmPassword = $state(false);
    let errorMsg = $state("");
    let passwordError = $state("");
    let loading = $state(false);

    const auth = getAuthStore();

    async function handleSubmit(e: Event) {
        e.preventDefault();
        loading = true;
        errorMsg = "";
        passwordError = "";

        if (!isLogin && password !== confirmPassword) {
            passwordError = "Passwords do not match";
            loading = false;
            return;
        }

        try {
            if (isLogin) {
                const user = await login(email, password);
                auth.setUser(user);
            } else {
                const user = await signup(username, email, password);
                auth.setUser(user);
            }
            goto("/modes");
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
                <div class="relative">
                    <input
                        id="password"
                        type={showPassword ? "text" : "password"}
                        placeholder="Password"
                        bind:value={password}
                        required
                        class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all pr-12"
                    />
                    <button
                        type="button"
                        onclick={() => (showPassword = !showPassword)}
                        class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors p-1"
                        aria-label={showPassword
                            ? "Hide password"
                            : "Show password"}
                    >
                        {#if showPassword}
                            <EyeOff size={20} />
                        {:else}
                            <Eye size={20} />
                        {/if}
                    </button>
                </div>
            </div>

            {#if !isLogin}
                <div class="space-y-2">
                    <label
                        for="confirmPassword"
                        class="block text-sm text-gray-400"
                        >Confirm Password</label
                    >
                    <div class="relative">
                        <input
                            id="confirmPassword"
                            type={showConfirmPassword ? "text" : "password"}
                            placeholder="Confirm Password"
                            bind:value={confirmPassword}
                            required
                            class="w-full px-4 py-3 bg-[#1a1a1a] border border-gray-800 rounded-lg text-white placeholder:text-gray-600 focus:outline-none focus:ring-2 focus:ring-gray-700 focus:border-transparent transition-all pr-12"
                        />
                        <button
                            type="button"
                            onclick={() =>
                                (showConfirmPassword = !showConfirmPassword)}
                            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-white transition-colors p-1"
                            aria-label={showConfirmPassword
                                ? "Hide password"
                                : "Show password"}
                        >
                            {#if showConfirmPassword}
                                <EyeOff size={20} />
                            {:else}
                                <Eye size={20} />
                            {/if}
                        </button>
                    </div>
                    {#if passwordError}
                        <p class="text-red-500 text-sm mt-1">{passwordError}</p>
                    {/if}
                </div>
            {/if}

            {#if errorMsg}
                <p class="text-red-500 text-sm">{errorMsg}</p>
            {/if}

            <button
                type="submit"
                disabled={loading || (!isLogin && password !== confirmPassword)}
                class="w-full px-6 py-3 bg-[#d4a933] hover:bg-[#e0b840] text-black font-semibold rounded-lg transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
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
