<script lang="ts">
    import { onMount } from "svelte";
    import { RotateCcw, Info } from "lucide-svelte";
    import {
        getGameState,
        submitGuess,
        resetGame,
        type GameSession,
    } from "$lib/utils/api";
    import GameBoard from "$lib/components/GameBoard.svelte";
    import SummaryBox from "$lib/components/SummaryBox.svelte"; // now consistent
    import ModeButton from "$lib/components/ModeButton.svelte";

    // State
    let session = $state<GameSession | null>(null);
    let currentGuess = $state("");
    let loading = $state(false);
    let errorMsg = $state("");

    // Visual Filters (Experimental Modes)
    let disableGreen = $state(false);
    let disableYellow = $state(false);

    // Summary Box Toggles
    let showGreenSummary = $state(true);
    let showYellowSummary = $state(true);
    let showInstructions = $state(false);

    onMount(async () => {
        try {
            loading = true;
            session = await getGameState();
        } catch (e) {
            console.error(e);
            errorMsg = "Failed to load game.";
        } finally {
            loading = false;
        }
    });

    async function handleKeydown(e: KeyboardEvent) {
        if (!session || session.status !== "IN_PROGRESS" || loading) return;
        if (e.metaKey || e.ctrlKey || e.altKey) return;

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
            currentGuess = "";
        } catch (e: any) {
            errorMsg = e.message;
            setTimeout(() => (errorMsg = ""), 3000); // Clear error after 3s
        } finally {
            loading = false;
        }
    }

    async function reset() {
        if (!confirm("Start a new game?")) return;
        try {
            loading = true;
            session = await resetGame();
            currentGuess = "";
            errorMsg = "";
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
    <div class="w-full max-w-6xl flex flex-col items-center gap-8">
        <!-- Header -->
        <div class="flex items-center justify-between w-full max-w-4xl">
            <button
                onclick={() => (showInstructions = !showInstructions)}
                class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-white"
                aria-label="Instructions"
            >
                <Info size={24} />
            </button>
            <h1 class="text-3xl sm:text-4xl font-bold tracking-wide">HARDLE</h1>
            <button
                onclick={reset}
                class="p-2 hover:bg-[#3a3a3c] rounded transition-colors text-white"
                aria-label="Reset"
            >
                <RotateCcw size={24} />
            </button>
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
                    <li>
                        • Use Mode buttons to suppress colors visually
                        (Experimental).
                    </li>
                </ul>
            </div>
        {/if}

        <!-- Main Game Area -->
        <div
            class="flex flex-col lg:flex-row items-start justify-center gap-8 w-full"
        >
            <!-- Game Board -->
            <div class="flex flex-col items-center gap-3">
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
            <div class="flex flex-col items-center gap-3">
                <SummaryBox
                    rows={getRowCounts()}
                    showGreen={showGreenSummary}
                    showYellow={showYellowSummary}
                    onToggleGreen={() => (showGreenSummary = !showGreenSummary)}
                    onToggleYellow={() =>
                        (showYellowSummary = !showYellowSummary)}
                />
                <p class="text-xs text-gray-500">Live count tracker</p>
            </div>
        </div>

        <!-- Control Buttons (Mode) -->
        <div class="flex flex-col sm:flex-row gap-4 w-full max-w-2xl mt-4">
            <ModeButton
                mode="green"
                disabled={disableGreen}
                onclick={() => (disableGreen = !disableGreen)}
            />
            <ModeButton
                mode="yellow"
                disabled={disableYellow}
                onclick={() => (disableYellow = !disableYellow)}
            />
        </div>
    </div>
</div>
