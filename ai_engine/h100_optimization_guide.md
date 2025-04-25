# Optimizing HunyuanVideo on H100 GPUs

This guide covers optimization techniques for running the HunyuanVideo model on NVIDIA H100 GPUs to achieve maximum performance.

## H100-Specific Optimizations

H100 GPUs offer significant performance improvements over previous generations with features like:

- TF32 precision support
- Transformer Engine for faster attention operations
- FP8 support for reduced memory usage
- 80GB HBM3 memory (in SXM version)

## Memory Optimization Techniques

1. **Use FP8 Quantization**
   
   HunyuanVideo provides FP8 weights which save about 10GB of GPU memory:
   ```bash
   python optimized_hunyuan_generator.py \
       --prompt "Your prompt here" \
       --use-fp8 \
       --fp8-weights-path /path/to/weights/hunyuanvideo_fp8.pt
   ```

2. **Multi-GPU Sequence Parallelism**
   
   For higher resolution videos, use multiple GPUs with Ulysses parallelism:
   ```bash
   python optimized_hunyuan_generator.py \
       --prompt "Your prompt here" \
       --use-ulysses \
       --gpu-count 8 \
       --ulysses-degree 8 \
       --ring-degree 1
   ```

   Supported configurations for 1280x720 video with 129 frames:
   - 8 GPUs: 8x1, 4x2, 2x4, 1x8 (ulysses x ring)
   - 4 GPUs: 4x1, 2x2, 1x4
   - 2 GPUs: 2x1, 1x2

3. **Gradient Checkpointing**
   
   Already enabled in the model, this reduces memory usage during inference.

## Speed Optimization Techniques

1. **Optimize CUDA Settings**
   
   The `optimize_cuda_settings()` function in our script applies the following optimizations:
   - Enables TF32 precision
   - Sets cudnn benchmark mode
   - Disables deterministic algorithms for speed
   - Sets memory allocation parameters

2. **Batch Processing**
   
   Process multiple prompts efficiently:
   ```bash
   python optimized_hunyuan_generator.py \
       --prompts-file your_prompts.txt \
       --use-fp8 \
       --fp8-weights-path /path/to/weights/hunyuanvideo_fp8.pt
   ```

3. **Optimize Inference Steps**
   
   Reduce the number of steps for faster generation (at potential quality cost):
   ```bash
   python optimized_hunyuan_generator.py \
       --prompt "Your prompt here" \
       --steps 30
   ```

## Resolution Trade-offs

Supported resolutions and their performance characteristics:

| Resolution | Relative Memory | Relative Speed | Quality |
|------------|----------------|----------------|---------|
| 1280x720   | Very High      | Slower         | Highest |
| 960x544    | Medium         | Faster         | Good    |
| 720x720    | Medium         | Faster         | Good    |

## Memory Management

The script implements proper memory management:
- Clears GPU cache after each generation
- Monitors memory usage
- Handles failures gracefully

## Example Usage Scenarios

### Maximum Quality (Single H100)

```bash
python optimized_hunyuan_generator.py \
    --prompt "A cat walks on the grass, realistic style." \
    --width 1280 \
    --height 720 \
    --video-length 129 \
    --steps 50 \
    --use-fp8 \
    --fp8-weights-path /path/to/weights/hunyuanvideo_fp8.pt
```

### Maximum Speed (Multiple H100s)

```bash
python optimized_hunyuan_generator.py \
    --prompt "A cat walks on the grass, realistic style." \
    --width 960 \
    --height 544 \
    --video-length 129 \
    --steps 30 \
    --use-ulysses \
    --gpu-count 8 \
    --ulysses-degree 8 \
    --ring-degree 1
```

### Batch Processing

```bash
python optimized_hunyuan_generator.py \
    --prompts-file prompts.txt \
    --width 960 \
    --height 544 \
    --use-fp8 \
    --fp8-weights-path /path/to/weights/hunyuanvideo_fp8.pt
```

## Monitoring

The script logs detailed information about:
- GPU memory usage before and after generation
- Generation time for each prompt
- Success/failure statistics

## Additional Tips

1. When working with H100 GPUs, ensure you're using CUDA 12.0+ and PyTorch 2.0+ for best performance
2. Use the `PYTORCH_CUDA_ALLOC_CONF` environment variable to tune memory allocation behavior
3. Clear CUDA cache between generations to prevent memory fragmentation
4. Consider using smaller resolutions for draft generations before final high-quality renders 