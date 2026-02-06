<script lang="ts">
    import { onMount } from "svelte";
    import { RotateCcw, Info, LogOut, Trophy } from "lucide-svelte";
    import DiscordIcon from "$lib/components/icons/DiscordIcon.svelte";
    import { goto } from "$app/navigation";
    import {
        getGameState,
        submitGuess,
        resetGame,
        logout,
        getMe,
        type GameSession,
    } from "$lib/utils/api";

    import { getAuthStore } from "$lib/state/auth.svelte";
    import GameBoard from "$lib/components/GameBoard.svelte";
    import SummaryBox from "$lib/components/SummaryBox.svelte";
    import RoughWorkPanel from "$lib/components/RoughWorkPanel.svelte";
    import Leaderboard from "$lib/components/Leaderboard.svelte";

    const auth = getAuthStore();

    // State
    let session = $state<GameSession | null>(null);
    let currentGuess = $state("");
    let loading = $state(false);
    let errorMsg = $state("");

    // Visual Filters (Experimental Modes) - Hidden in UI but logic kept dormant
    let disableGreen = $state(true);
    let disableYellow = $state(true);

    // Modal States
    let showInstructions = $state(false);
    let showLeaderboard = $state(false);
    let showEndgameModal = $state(false);

    onMount(async () => {
        // Auth Check
        if (!auth.isAuthenticated && !auth.isLoading) {
            goto("/");
            return;
        }

        try {
            loading = true;
            session = await getGameState();
            if (
                session &&
                (session.status === "WIN" || session.status === "LOSE")
            ) {
                showEndgameModal = true;
            }
        } catch (e) {
            console.error(e);
            errorMsg = "Failed to load game.";
        } finally {
            loading = false;
        }
    });

    // Reactive check for auth in case of logout
    $effect(() => {
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

    async function handleKeydown(e: KeyboardEvent) {
        if (!session || session.status !== "IN_PROGRESS" || loading) return;
        if (e.metaKey || e.ctrlKey || e.altKey) return;
        if (showLeaderboard || showEndgameModal) return; // Prevent playing while modal is open

        // Ignore typing in input fields (RoughWorkPanel)
        if (
            e.target instanceof HTMLInputElement ||
            e.target instanceof HTMLTextAreaElement
        )
            return;

        if (e.key === "Backspace") {
            currentGuess = currentGuess.slice(0, -1);
            return;
        }

        if (e.key === "Enter") {
            if (currentGuess.length !== 5) {
                errorMsg = "Not enough letters";
                setTimeout(() => (errorMsg = ""), 2000);
                return;
            }
            await submit();
            return;
        }

        if (/^[a-zA-Z]$/.test(e.key) && currentGuess.length < 5) {
            currentGuess += e.key.toUpperCase();
        }
    }

    async function submit() {
        if (!session) return;
        try {
            loading = true;
            errorMsg = "";
            session = await submitGuess(session.id, currentGuess);
            if (session.status === "WIN" || session.status === "LOSE") {
                // Refresh User Points
                if (auth.isAuthenticated) {
                    try {
                        const user = await getMe();
                        auth.setUser(user);
                    } catch (err) {
                        console.error("Failed to refresh points", err);
                    }
                }
                showEndgameModal = true;
            }
            currentGuess = "";
        } catch (e: any) {
            errorMsg = e.message;
            setTimeout(() => (errorMsg = ""), 3000); // Clear error after 3s
        } finally {
            loading = false;
        }
    }

    async function reset(skipConfirm = false) {
        if (!skipConfirm && !confirm("Start a new game?")) return;
        try {
            loading = true;
            session = await resetGame();
            currentGuess = "";
            errorMsg = "";
            showEndgameModal = false;
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    }

    function getRowCounts() {
        if (!session) return [];
        return Array(6)
            .fill(null)
            .map((_, i) => {
                const guess = session!.guesses[i];
                if (!guess) return { greenCount: 0, yellowCount: 0 };

                const greenCount = guess.colors.filter((c) => c === 2).length;
                const yellowCount = guess.colors.filter((c) => c === 1).length;
                return { greenCount, yellowCount };
            });
    }
</script>

<svelte:window onkeydown={handleKeydown} />

<div
    class="min-h-screen bg-[#121213] text-white flex items-center justify-center p-4 font-sans"
>
    <!-- Modal Overlay (Endgame) -->
    {#if showEndgameModal && session}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
        >
            <div
                class="w-full max-w-sm bg-[#1e1e1e] border border-gray-700 rounded-lg p-8 text-center space-y-8 shadow-2xl"
            >
                <h2
                    class="text-3xl font-bold {session.status === 'WIN'
                        ? 'text-green-500'
                        : 'text-red-500'}"
                >
                    {session.status === "WIN" ? "Well done!" : "Game Over"}
                </h2>

                <div class="space-y-2">
                    <p class="text-xl text-white">
                        Your word was <span
                            class="font-mono font-bold text-[#d4a933]"
                            >{session.target_word || "???"}</span
                        >
                    </p>
                    <p class="text-lg text-white">
                        You gained <span class="font-bold"
                            >{session.status === "WIN" ? "5" : "0"} points</span
                        >.
                    </p>
                    <p class="text-sm text-gray-400">
                        Come back tomorrow to improve your rank.
                    </p>
                </div>

                <div class="flex flex-col gap-3">
                    <button
                        onclick={() => reset(true)}
                        class="w-full px-6 py-3 bg-[#d4a933] hover:bg-[#e0b840] rounded-lg transition-colors text-black font-bold text-lg"
                    >
                        Play Again
                    </button>

                    <button
                        onclick={() => (showEndgameModal = false)}
                        class="w-full px-6 py-2 bg-transparent hover:bg-white/5 rounded-lg transition-colors text-gray-400 hover:text-white"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    {/if}

    <!-- Modal Overlay (Leaderboard) -->
    {#if showLeaderboard}
        <div
            class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm"
            role="dialog"
            aria-modal="true"
            onclick={() => (showLeaderboard = false)}
            onkeydown={(e) => e.key === "Escape" && (showLeaderboard = false)}
            tabindex="0"
        >
            <div
                class="w-full max-w-lg"
                onclick={(e) => e.stopPropagation()}
                role="document"
                tabindex="0"
            >
                <Leaderboard />
                <div class="mt-4 text-center">
                    <button
                        class="text-sm text-gray-500 hover:text-white"
                        onclick={() => (showLeaderboard = false)}>Close</button
                    >
                </div>
            </div>
        </div>
    {/if}

    <div class="w-full max-w-7xl flex flex-col items-center gap-8">
        <!-- Header -->
        <div
            class="flex items-center justify-between w-full max-w-4xl relative min-h-[64px]"
        >
            <!-- Left: Instructions -->
            <div class="flex items-center">
                <button
                    onclick={() => (showInstructions = !showInstructions)}
                    class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-white"
                    aria-label="Instructions"
                >
                    <Info size={24} />
                </button>
            </div>

            <!-- Center: Title & User Info Stacked -->
            <div
                class="absolute inset-0 flex flex-col items-center justify-center pointer-events-none"
            >
                <h1
                    class="text-3xl sm:text-4xl font-bold tracking-wide pointer-events-auto"
                >
                    HARDLE
                </h1>
                {#if auth.user}
                    <div
                        class="text-[10px] sm:text-xs text-gray-500 font-mono uppercase tracking-widest mt-1"
                    >
                        PLAYING AS {auth.user.username} | {auth.user.points} PTS
                    </div>
                {/if}
            </div>

            <!-- Right: Controls -->
            <div class="flex items-center gap-2">
                <!-- Trophy (Leaderboard) -->
                <button
                    onclick={() => (showLeaderboard = true)}
                    class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-[#d4a933]"
                    aria-label="Leaderboard"
                >
                    <Trophy size={24} />
                </button>

                <!-- Discord -->
                <a
                    href="https://discord.gg/nxYPEZT4"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="p-2 hover:bg-[#5865F2]/20 text-[#5865F2] rounded transition-colors"
                    aria-label="Discord"
                >
                    <DiscordIcon size={24} />
                </a>

                <div class="w-px h-6 bg-gray-700 mx-1"></div>

                <button
                    onclick={() => reset()}
                    class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-white"
                    aria-label="Reset"
                >
                    <RotateCcw size={24} />
                </button>
                <button
                    onclick={handleLogout}
                    class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-red-400"
                    aria-label="Logout"
                >
                    <LogOut size={24} />
                </button>
            </div>
        </div>

        <!-- Error Toast -->
        {#if errorMsg}
            <div
                class="fixed top-20 bg-red-500 text-white px-4 py-2 rounded shadow-lg z-50 animate-bounce"
            >
                {errorMsg}
            </div>
        {/if}

        {#if showInstructions}
            <div
                class="w-full max-w-2xl bg-[#1e1e1e] border border-[#3a3a3c] rounded-lg p-6 text-sm"
            >
                <h2 class="text-xl font-bold mb-3">How to Play</h2>
                <ul class="space-y-2 text-gray-300">
                    <li>
                        • Keyboard Input Only. Type to guess. Enter to submit.
                    </li>
                    <li>
                        • <span class="text-[#6aaa64]">Green</span> = Correct position
                    </li>
                    <li>
                        • <span class="text-[#c9b458]">Yellow</span> = Wrong position
                    </li>
                </ul>
            </div>
        {/if}

        <!-- Main Game Area -->
        <div
            class="flex flex-col lg:flex-row items-start justify-center gap-8 w-full"
        >
            <!-- Game Board -->
            <div class="flex flex-col items-center gap-3 order-1">
                {#if session}
                    <GameBoard
                        guesses={session.guesses}
                        {currentGuess}
                        status={session.status}
                        {disableGreen}
                        {disableYellow}
                    />
                {/if}
                <p class="text-xs text-gray-500">Keyboard input only</p>
            </div>

            <!-- Summary Box (Counts) -->
            <div class="flex flex-col items-center gap-3 order-2">
                <SummaryBox rows={getRowCounts()} />
                <p class="text-xs text-gray-500">Live count tracker</p>
            </div>

            <!-- Rough Work Panel -->
            <div class="flex flex-col items-center gap-3 order-3">
                <RoughWorkPanel />
                <p class="text-xs text-gray-500">Scratch pad for notes</p>
            </div>
        </div>
    </div>
</div>
