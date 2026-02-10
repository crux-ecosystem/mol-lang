# Tutorial: Neural Simulation

Use MOL's cognitive types to simulate a simple neural network.

## Concepts

MOL has built-in types for neural computation:

- **Node** — a neuron with a weight, connections, and generation counter
- **Thought** — an idea with a confidence score
- **Memory** — persistent storage with decay
- **Stream** — event pub/sub

## Step 1: Create a Network

```text
-- Create neurons
let input1 be Node("input_1", 0.5)
let input2 be Node("input_2", 0.7)
let hidden be Node("hidden_1", 0.3)
let output be Node("output", 0.9)

-- Wire them up
link input1 to hidden
link input2 to hidden
link hidden to output

show "Network created:"
show input1
show input2
show hidden
show output
```

## Step 2: Evolve the Network

```text
-- Evolve nodes (increases weight by 10%, increments generation)
evolve input1
evolve input2
evolve hidden
evolve output

show ""
show "After evolution:"
show "input_1 weight: " + to_text(input1.weight) + " gen: " + to_text(input1.generation)
show "input_2 weight: " + to_text(input2.weight) + " gen: " + to_text(input2.generation)
show "hidden  weight: " + to_text(hidden.weight) + " gen: " + to_text(hidden.generation)
show "output  weight: " + to_text(output.weight) + " gen: " + to_text(output.generation)
```

## Step 3: Process Signals

```text
-- Create a thought signal
let signal be Thought("Pattern: 101", 0.8)
show ""
show "Processing signal: " + signal.content

-- Process through the network
process hidden with signal
show "Processed through hidden layer"
```

## Step 4: Memory and Learning

```text
-- Store important results
let result be Memory("training_result", signal)
show ""
show "Stored: " + result.key + " = " + to_text(result.value.content)

-- Recall strengthens the memory
let recalled be recall(result)
show "Recalled with strength: " + to_text(result.strength)
```

## Step 5: Event-Driven Training

```text
-- Set up event listeners
listen "epoch_complete" do
  show "  → Epoch finished, evolving network..."
  evolve hidden
  evolve output
end

-- Simulate training epochs
show ""
show "Training..."
for epoch in range(3) do
  show "Epoch " + to_text(epoch + 1)
  trigger "epoch_complete"
end

show ""
show "Final weights:"
show "hidden: " + to_text(round(hidden.weight, 4))
show "output: " + to_text(round(output.weight, 4))
```

## Complete Simulation

```text
-- ═══ Neural Simulation in MOL ═══

-- Build network
let sensor be Node("sensor", 0.6)
let processor be Node("processor", 0.4)
let actuator be Node("actuator", 0.8)

link sensor to processor
link processor to actuator

-- Training loop
show "═══ Neural Training ═══"
show ""

for gen in range(5) do
  evolve sensor
  evolve processor
  evolve actuator

  let confidence be sensor.weight * processor.weight * actuator.weight
  let thought be Thought("Generation " + to_text(gen + 1), confidence)
  
  show "Gen " + to_text(gen + 1) + " | Confidence: " + to_text(round(confidence, 4))

  if confidence > 0.5 then
    show "  → Network is learning!"
  end
end

-- Store final state
let final_state be Memory("trained_model", {
  "sensor": sensor.weight,
  "processor": processor.weight,
  "actuator": actuator.weight,
  "generations": sensor.generation
})

show ""
show "Training complete!"
show "Final state stored in memory: " + final_state.key

-- Emit completion
emit "training_complete"
show ""
show "═══ Simulation Complete ═══"
```

## Run It

```bash
mol run neural_sim.mol
```

## Key Takeaways

1. **Node** provides neural primitives with weights and evolution
2. **link** connects nodes into networks
3. **evolve** simulates learning (weight growth + generation tracking)
4. **Thought** carries signals with confidence scores
5. **Memory** persists results with recall strength
6. **Events** (listen/trigger) enable reactive training loops
