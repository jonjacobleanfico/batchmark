# batchmark

Simple TypeScript utility for benchmarking batch processing pipelines with structured output.

## Installation

```bash
npm install batchmark
```

## Usage

```typescript
import { Batchmark } from "batchmark";

const bench = new Batchmark();

const results = await bench.run({
  name: "csv-pipeline",
  batchSize: 100,
  task: async (batch) => {
    // your processing logic here
    return processBatch(batch);
  },
});

console.log(results.summary());
// {
//   name: "csv-pipeline",
//   totalItems: 1000,
//   duration: "3.24s",
//   throughput: "308 items/sec",
//   p50: "48ms",
//   p95: "91ms"
// }
```

### Options

| Option      | Type     | Default | Description                        |
|-------------|----------|---------|------------------------------------|
| `name`      | `string` | —       | Label for the benchmark run        |
| `batchSize` | `number` | `50`    | Number of items per batch          |
| `warmup`    | `number` | `0`     | Warmup iterations before measuring |
| `output`    | `string` | `json`  | Output format (`json` or `table`)  |

## Output

Results are written to `./batchmark-results/` by default, with one structured JSON file per run. Pass `output: "table"` to print a formatted summary to stdout instead.

## License

MIT