<script lang="ts">
    interface Props {
        mode: "green" | "yellow";
        disabled: boolean;
        onclick: () => void;
    }

    let { mode, disabled, onclick } = $props<Props>();

    const isGreen = $derived(mode === "green");
    const label = $derived(
        isGreen ? "DISABLE GREEN MODE" : "DISABLE YELLOW MODE",
    );
    const color = $derived(isGreen ? "#6aaa64" : "#c9b458");
</script>

<button
    {onclick}
    class={`
    flex-1 py-4 px-8 font-bold text-lg tracking-wide transition-all duration-200
    ${disabled ? "bg-[#3a3a3c] text-gray-500 opacity-50" : "text-white hover:opacity-90 active:scale-98"}
  `}
    style:background-color={disabled ? "#3a3a3c" : color}
>
    {disabled ? label.replace("DISABLE", "DISABLED") : label}
</button>
