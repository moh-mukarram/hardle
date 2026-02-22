<script lang="ts">
    import { onMount } from "svelte";
    import { ChevronUp, ChevronDown } from "lucide-svelte";
    import Header from "$lib/components/Header.svelte";
    import GameGrid from "$lib/components/GameGrid.svelte";
    import Keyboard from "$lib/components/Keyboard.svelte";
    import DecryptionPanel from "$lib/components/DecryptionPanel.svelte";
    import OutcomeMessage from "$lib/components/OutcomeMessage.svelte";
    import SessionTimer from "$lib/components/SessionTimer.svelte";
    import ClearancePanel from "$lib/components/ClearancePanel.svelte";
    import LeaderboardPanel from "$lib/components/LeaderboardPanel.svelte";
    import Leaderboard from "$lib/components/Leaderboard.svelte";
    import { getAuthStore } from "$lib/state/auth.svelte";
    import { API_BASE, ensureCsrfToken } from "$lib/utils/api";
    import { userStore } from "$lib/stores/user";
    import "$lib/styles/daily.css";

    const auth = getAuthStore();

    // Word list for the game

    // Session time limit in seconds (5 minutes)
    const SESSION_TIME_LIMIT = 300;

    type LetterState = "correct" | "present" | "absent" | "empty" | "current";

    interface Guess {
        letters: string[];
        states: LetterState[];
        colors?: number[];
    }

    interface OutcomeMessages {
        primary: string;
        secondary: string;
    }

    let targetWord = $state("");
    let guesses = $state<Guess[]>([]);
    let currentGuess = $state(0);
    let currentLetter = $state(0);
    let gameStatus = $state<"playing" | "won" | "lost">("playing");
    let statusMessage = $state("AWAITING INPUT");
    let keyStates = $state<Map<string, LetterState>>(new Map());
    let panelOpen = $state(false);
    let timeRemaining = $state(SESSION_TIME_LIMIT);
    let isProcessing = $state(false);
    let resolvingTileIndex = $state(-1);
    let enterPressed = $state(false);
    let outcomeMessages = $state<OutcomeMessages | null>(null);
    let lossReason = $state<"attempts" | "time" | null>(null);

    // Leaderboard state
    let leaderboardOpen = $state(false);
    let leaderboardRef: LeaderboardPanel | undefined = $state();

    // Session timer
    $effect(() => {
        if (gameStatus !== "playing") return;

        const timer = setInterval(() => {
            if (gameStatus !== "playing") {
                clearInterval(timer);
                return;
            }
            if (timeRemaining <= 1) {
                // Call backend to expire session
                expireSession();
                timeRemaining = 0;
                clearInterval(timer);
            } else {
                timeRemaining -= 1;
            }
        }, 1000);

        return () => clearInterval(timer);
    });

    function handleKeyPress(key: string) {
        if (gameStatus !== "playing" || isProcessing) return;

        if (key === "ENTER") {
            if (currentLetter === 5) {
                enterPressed = true;
                setTimeout(() => (enterPressed = false), 200);
                submitGuess();
            }
        } else if (key === "BACKSPACE") {
            if (currentLetter > 0) {
                guesses[currentGuess].letters[currentLetter - 1] = "";
                guesses[currentGuess].states[currentLetter - 1] = "empty";
                currentLetter -= 1;
            }
        } else if (key.length === 1 && /[A-Z]/.test(key)) {
            if (currentLetter < 5) {
                guesses[currentGuess].letters[currentLetter] = key;
                guesses[currentGuess].states[currentLetter] = "current";
                currentLetter += 1;
            }
        }
    }

    let sessionId = $state("");
    let displayedPoints = $state(0);

    async function loadGameState() {
        try {
            const res = await fetch(`/api/game/state?mode=daily`, {
                credentials: "include",
            });
            if (res.ok) {
                const data = await res.json();
                sessionId = data.id;
                gameStatus =
                    data.status === "IN_PROGRESS"
                        ? "playing"
                        : data.status.toLowerCase();

                // Re-hydrate blank structure for unified rendering
                const baseGuesses = Array(6)
                    .fill(null)
                    .map(() => ({
                        letters: ["", "", "", "", ""],
                        states: [
                            "empty",
                            "empty",
                            "empty",
                            "empty",
                            "empty",
                        ] as LetterState[],
                        colors: [0, 0, 0, 0, 0], // Native array for standard color modes
                    }));
                // Hydrate guesses and inject standard mode overrides
                data.guesses.forEach((g: any, i: number) => {
                    if (i < 6) {
                        const letters = g.word.split("");
                        let colors = g.colors;

                        const states = colors.map((c: number) =>
                            c === 2
                                ? "correct"
                                : c === 1
                                  ? "present"
                                  : "absent",
                        );

                        baseGuesses[i] = { letters, states, colors };
                    }
                });
                guesses = baseGuesses;
                currentGuess = data.guesses.length;

                // Hydrate Keyboard
                const newKeyStates = new Map(keyStates);
                data.guesses.forEach((g: any) => {
                    g.word.split("").forEach((char: string, index: number) => {
                        const color = g.colors[index];
                        const state =
                            color === 2
                                ? "correct"
                                : color === 1
                                  ? "present"
                                  : "absent";
                        const currentState = newKeyStates.get(char);
                        if (state === "correct")
                            newKeyStates.set(char, "correct");
                        else if (
                            state === "present" &&
                            currentState !== "correct"
                        )
                            newKeyStates.set(char, "present");
                        else if (state === "absent" && !currentState)
                            newKeyStates.set(char, "absent");
                    });
                });
                keyStates = newKeyStates;

                // Handle Game Over State/Result Rehydration
                if (data.status !== "IN_PROGRESS") {
                    targetWord = data.target_word || "";

                    if (data.status === "WIN") {
                        gameStatus = "won";
                        statusMessage = "ACCESS GRANTED";
                        outcomeMessages = {
                            primary: "SYSTEM BREACHED",
                            secondary: "ACCESS GRANTED — COMPLETE",
                        };
                    } else {
                        gameStatus = "lost";
                        statusMessage = "DECRYPTION FAILED";
                        outcomeMessages = {
                            primary: "DECRYPTION FAILED",
                            secondary: "KEY COULD NOT BE DERIVED",
                        };
                    }
                }
            }
        } catch (e) {
            console.error("Failed to load game state", e);
        }
    }

    async function expireSession() {
        if (gameStatus !== "playing") return;

        try {
            const res = await fetch(`/api/game/guess?session_id=${sessionId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ guess: "__TIMEOUT__" }),
                credentials: "include",
            });

            if (res.ok) {
                const data = await res.json();
                handleGameEnd(data.results);
            }
        } catch (e) {
            console.error("Failed to expire session", e);
        }
    }

    function handleGameEnd(results: any) {
        if (!results) return;

        targetWord = results.solution || targetWord; // Fallback to existing if missing
        displayedPoints = results.points_delta || 0;

        // Update user total points in store
        userStore.update((u) => {
            u.points += results.points_delta;
            return u;
        });

        // Sync auth store with new total
        if (auth.user) {
            auth.setUser({ ...auth.user, points: $userStore.points });
        }

        // Refresh leaderboard to reflect new scores
        if (leaderboardRef) {
            leaderboardRef.refresh();
        }

        if (results.outcome === "WIN") {
            gameStatus = "won";
            statusMessage = "ACCESS GRANTED";
            outcomeMessages = {
                primary: "SYSTEM BREACHED",
                secondary: "ACCESS GRANTED — COMPLETE",
            };
        } else if (results.outcome === "SESSION_EXPIRED") {
            gameStatus = "lost";
            lossReason = "time";
            statusMessage = "SESSION EXPIRED";
            outcomeMessages = {
                primary: "SESSION EXPIRED",
                secondary: "THE WORLD COULD NOT BE SAVED",
            };
        } else {
            gameStatus = "lost";
            lossReason = "attempts";
            statusMessage = "DECRYPTION FAILED";
            outcomeMessages = {
                primary: "DECRYPTION FAILED",
                secondary: "KEY COULD NOT BE DERIVED",
            };
        }
    }

    async function submitGuess() {
        isProcessing = true;
        statusMessage = "PROCESSING GUESS";

        const guessWord = guesses[currentGuess].letters.join("");

        try {
            const res = await fetch(`/api/game/guess?session_id=${sessionId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ guess: guessWord }),
                credentials: "include",
            });

            if (!res.ok) {
                const err = await res.json();
                statusMessage = err.message || "ERROR";
                isProcessing = false;
                // Shake animation could trigger here
                return;
            }

            const data = await res.json();
            const lastGuess = data.guesses[data.guesses.length - 1];
            const newStates = lastGuess.colors.map((c: number) =>
                c === 2 ? "correct" : c === 1 ? "present" : "absent",
            );

            guesses[currentGuess].colors = lastGuess.colors;

            const finalizeTurn = () => {
                resolvingTileIndex = -1;

                // Update keyboard states
                const newKeyStates = new Map(keyStates);
                guessWord.split("").forEach((letter, i) => {
                    const currentState = newKeyStates.get(letter);
                    const newState = newStates[i];

                    if (newState === "correct") {
                        newKeyStates.set(letter, "correct");
                    } else if (
                        newState === "present" &&
                        currentState !== "correct"
                    ) {
                        newKeyStates.set(letter, "present");
                    } else if (newState === "absent" && !currentState) {
                        newKeyStates.set(letter, "absent");
                    }
                });
                keyStates = newKeyStates;

                // Check win/loss from Backend Status
                if (data.status !== "IN_PROGRESS") {
                    const results = data.results || {
                        outcome: data.status,
                        solution: data.target_word,
                        points_delta: 0,
                        greens_count: 0,
                        yellows_count: 0,
                    };
                    handleGameEnd(results);
                } else {
                    currentGuess += 1;
                    currentLetter = 0;
                    statusMessage = "AWAITING INPUT";
                }

                isProcessing = false;
            };

            // Animate tiles resolving sequentially
            let currentTile = 0;
            const revealInterval = setInterval(() => {
                if (currentTile < 5) {
                    resolvingTileIndex = currentTile;
                    guesses[currentGuess].states[currentTile] =
                        newStates[currentTile];
                    currentTile++;
                } else {
                    clearInterval(revealInterval);
                    finalizeTurn();
                }
            }, 150);
        } catch (e) {
            statusMessage = "CONNECTION ERROR";
            isProcessing = false;
        }
    }

    onMount(() => {
        ensureCsrfToken();
        loadGameState();

        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Enter") {
                handleKeyPress("ENTER");
            } else if (e.key === "Backspace") {
                handleKeyPress("BACKSPACE");
            } else if (/^[a-zA-Z]$/.test(e.key)) {
                handleKeyPress(e.key.toUpperCase());
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    });

    let greens = $derived(
        Math.min(
            guesses
                .slice(0, currentGuess + 1)
                .flatMap((g) => g.states.filter((s) => s === "correct")).length,
            10,
        ),
    );

    let yellows = $derived(
        Math.min(
            guesses
                .slice(0, currentGuess + 1)
                .flatMap((g) => g.states.filter((s) => s === "present")).length,
            10,
        ),
    );

    // Animated status message with ellipsis
    let animatedStatus = $state("AWAITING INPUT");
    $effect(() => {
        if (statusMessage === "PROCESSING GUESS" && isProcessing) {
            const interval = setInterval(() => {
                const dots = Math.floor((Date.now() / 400) % 4);
                animatedStatus = "PROCESSING GUESS" + ".".repeat(dots);
            }, 100);
            return () => clearInterval(interval);
        } else {
            animatedStatus = statusMessage;
        }
    });
</script>

<div class="min-h-screen text-cyan-400 font-mono flex flex-col">
    <Header
        {timeRemaining}
        sessionTimeLimit={SESSION_TIME_LIMIT}
        onLeaderboardOpen={() => (leaderboardOpen = true)}
    />

    <div
        class="flex flex-col lg:flex-row gap-4 lg:gap-6 px-4 lg:px-6 py-3 lg:py-4 max-w-[1600px] mx-auto flex-1 w-full"
    >
        <!-- Main game area -->
        <div class="flex-1 flex flex-col">
            <!-- Session info -->
            <div
                class="text-xs text-cyan-500/60 mb-2 lg:mb-4 border border-cyan-900/40 rounded px-3 py-2 bg-slate-900/20 font-mono"
            >
                <span class="text-cyan-400/70">[l0bed]</span>
                <span class="text-cyan-500/60">C:\\hardle</span>
                <span class="text-cyan-600/40 mx-2">›</span>
                <span class="text-cyan-500/50">06●08N 1 16</span>
            </div>

            <!-- Mobile timer - ABOVE grid -->
            <div class="lg:hidden text-center mb-2">
                <SessionTimer
                    {timeRemaining}
                    sessionTimeLimit={SESSION_TIME_LIMIT}
                    compact={true}
                    {gameStatus}
                />
            </div>

            <!-- Game grid -->
            <div class="flex-1 flex items-center justify-center mb-2 lg:mb-6">
                <GameGrid
                    {guesses}
                    currentRow={currentGuess}
                    {resolvingTileIndex}
                    {gameStatus}
                />
            </div>

            <!-- Status message - BELOW grid, ABOVE keyboard - Mobile -->
            <div
                class="lg:hidden text-xs text-cyan-400 mb-2 font-mono tracking-wider text-center min-h-[16px]"
            >
                {outcomeMessages ? outcomeMessages.primary : animatedStatus}
            </div>

            <!-- Keyboard - shown only when playing -->
            {#if gameStatus === "playing"}
                <Keyboard
                    onKeyPress={handleKeyPress}
                    {keyStates}
                    {enterPressed}
                    disabled={isProcessing}
                />
            {/if}

            <!-- Keyboard fade out on game end -->
            {#if gameStatus !== "playing"}
                <div class="h-0 overflow-hidden"></div>
            {/if}

            <!-- Outcome message (end state) - Desktop -->
            {#if outcomeMessages}
                <div class="hidden lg:block">
                    <OutcomeMessage
                        primary={outcomeMessages.primary}
                        secondary={outcomeMessages.secondary}
                        solution={targetWord}
                        pointsGained={displayedPoints}
                    />
                </div>
            {/if}

            <!-- Status message (playing state) - Desktop -->
            {#if !outcomeMessages}
                <div
                    class="hidden lg:flex text-sm text-cyan-400 mb-3 lg:mb-4 font-mono tracking-wider text-center lg:text-left min-h-[20px]"
                >
                    {animatedStatus}
                </div>
            {/if}

            <!-- Outcome message - Mobile (replaces keyboard) -->
            {#if outcomeMessages}
                <div class="lg:hidden mb-3">
                    <OutcomeMessage
                        primary={outcomeMessages.primary}
                        secondary={outcomeMessages.secondary}
                        solution={targetWord}
                        pointsGained={displayedPoints}
                        gameStatus={gameStatus === "playing"
                            ? "lost"
                            : gameStatus}
                    />
                </div>
            {/if}

            <!-- Clearance Panel - Mobile (after outcome) -->
            {#if outcomeMessages}
                <div class="lg:hidden mb-3">
                    <ClearancePanel
                        currentTotalPoints={$userStore.points}
                        pointsGained={displayedPoints}
                        gameStatus={gameStatus === "playing"
                            ? "won"
                            : gameStatus}
                    />
                </div>
            {/if}
        </div>

        <!-- Right panel - Desktop -->
        <div class="hidden lg:block w-full max-w-[280px]">
            {#if gameStatus === "playing"}
                <DecryptionPanel
                    {greens}
                    {yellows}
                    attemptsUsed={currentGuess}
                    {gameStatus}
                />
            {:else}
                <ClearancePanel
                    currentTotalPoints={$userStore.points}
                    pointsGained={displayedPoints}
                    {gameStatus}
                />
            {/if}
        </div>
    </div>

    <!-- Mobile Panel - Bottom Sheet -->
    <div class="lg:hidden fixed bottom-0 left-0 right-0 z-40">
        {#if gameStatus === "playing"}
            <!-- Toggle button -->
            <button
                onclick={() => (panelOpen = !panelOpen)}
                class="w-full bg-slate-900/95 border-t border-cyan-900/40 px-4 py-2.5 flex items-center justify-between"
            >
                <span class="text-xs tracking-widest text-cyan-400/80"
                    >[ DECRYPTION STATE ]</span
                >
                {#if panelOpen}
                    <ChevronDown class="w-4 h-4 text-cyan-400" />
                {:else}
                    <ChevronUp class="w-4 h-4 text-cyan-400" />
                {/if}
            </button>

            <!-- Panel content -->
            <div
                class={`bg-slate-900/95 border-t border-cyan-900/40 overflow-y-auto transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] ${
                    panelOpen ? "max-h-[60vh]" : "max-h-0"
                }`}
            >
                <div class="p-4">
                    <DecryptionPanel
                        {greens}
                        {yellows}
                        attemptsUsed={currentGuess}
                        {gameStatus}
                        isMobile={true}
                    />
                </div>
            </div>
        {/if}
    </div>
    <LeaderboardPanel
        bind:this={leaderboardRef}
        isOpen={leaderboardOpen}
        onClose={() => (leaderboardOpen = false)}
        currentPlayerPoints={$userStore.points}
    />
</div>
