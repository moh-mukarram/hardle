<script lang="ts">
    interface Props {
        letter: string;
        color: number; // 0=Gray, 1=Yellow, 2=Green, -1=Empty/Current
        size?: "md" | "lg";
        disabled?: boolean; // If true, rendering might be dimmed?
    }

    let { letter, color, size = "lg", disabled = false }: Props = $props();

    // Map backend colors to visual styles
    // 0 -> Gray (#3a3a3c)
    // 1 -> Yellow (#c9b458)
    // 2 -> Green (#6aaa64)
    // -1 -> Empty/Input (#121213)

    const getColorClass = (c: number) => {
        switch (c) {
            case 2: // Green
                return "bg-green-900/60 border-green-600 text-green-100 shadow-[var(--glow-tile-green)]";
            case 1: // Yellow
                return "bg-amber-900/60 border-amber-600 text-amber-100 shadow-[var(--glow-tile-amber)]";
            case 0: // Gray
                return "bg-slate-800/40 border-slate-700 text-slate-500";
            case 3: // Neutral Static (Very Hard Mode Phase 2)
                return "bg-slate-900/20 border-cyan-900/40 text-cyan-300";
            case -1: // Empty/Input
            default:
                return "border-cyan-500 text-cyan-300 bg-slate-900/40";
        }
    };

    const getSizeClass = (s: "md" | "lg") => {
        return s === "lg"
            ? "w-12 h-12 md:w-14 md:h-14 text-xl md:text-2xl"
            : "w-10 h-10 text-xl"; // For small preview if needed
    };
</script>

<div
    class={`
    flex items-center justify-center border-2 font-bold uppercase select-none transition-all duration-200
    ${getSizeClass(size)}
    ${getColorClass(color)}
    ${letter && color === -1 ? "animate-[borderPulse_80ms_ease-out]" : ""}
  `}
>
    {letter}
</div>
