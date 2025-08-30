# GPT2 Parallel Reasoning (gpt.c)

## 1. Background

Models in the GPT (Generative Pre-trained Transformers) series have ushered in a new era of artificial intelligence. From chatbots to multimodal models and embodied intelligence, AI is set to completely revolutionize the way human society operates. At its core, a "Large Language Model" like GPT is a function, `f`, that takes a "string of text" as input and outputs the "next most likely character." This "intelligent" function `f` has astonishing application scenarios, including serving as a copilot for "everything" (programming, operating system navigation, and even classroom learning) and enabling intelligent agents that can replace humans in various tasks. "Multimodal" models can even align text, images, sound, and touch with the vectors trained in language models, achieving an "intelligence" similar to that of humans.

Once trained, `f` is deployed in the cloud (on supercomputers) or on edge devices (such as phones and watches) and provides services through APIs. We foresee that AI inference services will become essential infrastructure for human society, much like water, electricity, and the cloud.

---

## 2\. Project Description

### 2.1 Overview

```bash
gpt [token]...
```

### 2.2 Description

Use the `gpt2_124M` model to complete an input sequence of tokens (integers) representing a piece of text. The program should output the subsequent possible tokens, resulting in a total of `n=10` tokens (including the input), which represent the "likely" continuation of the text in a probabilistic sense.

### 2.3 Explanation

GPT-2 is an early Transformer-based model that laid the technical foundation for OpenAI. Parallelization is one of the key techniques for improving the computational efficiency of large-scale models. The file `gpt.c` implements the "text completion" task of generative AI, and the framework code already provides a complete neural network inference implementation, trimmed down from [`llm.c`](https://github.com/karpathy/llm.c). By downloading `gpt2_124M.bin` into the project directory, the program will work correctly and perform text completion. By interacting with it, you can appreciate the rapid development of natural language processing. (GPT-2 is a model from 2019, and we are using the small 124M version, whose capabilities are no match for today's models, but you can still see that it can indeed generate "legitimate" sentences).

> ⚠️
> **You need to download the model manually.**
>
> The model file is large (\~500MB), so you need to download it into the project directory [ manually](https://huggingface.co/datasets/karpathy/llmc-starter-pack/resolve/main/gpt2_124M.bin). This file will not be tracked by git, nor will it be uploaded to the server.

You also need to provide a Python script, `chat.py`, which allows you to directly input a piece of text, perform tokenization, and then call the `gpt` command-line tool for completion. Yes, you are actually using a large language model that can generate text in this project\! The code has been fully prepared for you and works out of the box. In the example below, the number sequence "31373 612" corresponds to "Ladies and". As you can see, the language model has indeed generated readable text for us:

![gpt](gpt.gif)

Yes, even for such a small model, the single-threaded implementation struggles to perform inference on a CPU, let alone the "massive" GPT-3 (175 billion parameters) that came later. Neural network inference optimization is a very complex topic; here, we will try to take the first step towards parallelization:

> 🗒️
> **project Requirement: Parallelize `gpt.c`**
>
> Our `gpt.c` is serial code (though its functionality is unchanged) and can only utilize a single processor. You need to find the parts of the code that can be parallelized (and will benefit from it), convert them to a parallel implementation, and achieve the corresponding performance improvement.

In this project, you can use the threading library from the course (`thread.h` and `thread-sync.h`), which includes thread creation and cleanup, mutexes, semaphores, and condition variables. You can choose your preferred mechanisms for synchronization and mutual exclusion.

## 3\. Correctness Standard

> 🗒️
> **Correctness & Scalability**
>
> The behavior of your parallelized program should remain strictly consistent with the serial program we provide. (If you wish to "play around," you can go directly to the original repo). For example, we input + output a total of `n=10` tokens. You should keep this behavior unchanged.
>
> Adjustments to the order of computation resulting from parallelization may slightly affect the activation function values throughout the neural network, but as long as the final output token sequence (understood as text) is consistent, we consider it correct. Compared to the serial program, on a computer with `k` processors, you should achieve a nearly linear (`k` times) speedup for a large number of inference rounds, excluding the model loading time.

During online evaluation, `k≤4`. For real-world neural network training/inference systems, massively parallel processors like GPUs, which use a SIMT architecture, have a huge advantage over CPUs in terms of energy efficiency. Recalling the discussion on SIMT in the course, a warp of threads shares a single Program Counter, controlling multiple threads to execute instructions "in sync." In this scenario, for loading/storing large matrices and vectors, a single warp will generate a very long memory load (coalesced memory access). GPUs are also specially optimized for this memory access pattern—compared to the memory hierarchy designed for "logical programs" in CPUs, they have a much higher circuit and energy efficiency ratio.

In this project, you need to statically allocate threads (e.g., 4 workers), which will then complete the computational tasks. The threading library used during Online Judge testing is identical to the one in your project code.

## 4. Project Guide

### 4.1 How GPT-2 Works

First and foremost, the source code of `gpt.c` is the best teacher! It provides a "truly mathematically rigorous" description of the neural network. When we look at PyTorch code, it involves many built-in operators whose implementations you may not 100% understand. However, for a language with "flat" semantics like C, you can truly understand it completely! Additionally, we provide an external link and also recommend [*Understanding Deep Learning*](https://udlbook.github.io/udlbook/).

### 4.2 Finding Opportunities for Parallelization

How should you optimize your code? Before starting any optimization, first consider the famous quote by D. E. Knuth:

> Premature optimization is the root of all evil.

"Premature" not only means you shouldn't perform "arbitrary" optimizations during the code implementation process—which might yield minimal benefits while severely damaging your code's readability and maintainability—but it also means you shouldn't randomly modify your code to make optimizations based on assumptions. Similarly, these optimizations might harm readability and likely have little effect.

💡
**How to make the right optimizations?**

Here's a hint: *Everything is a state machine.* Following this line of thought, how should we approach the problem of performance optimization?

The answer is: we should observe the execution of the state machine. According to the 80/20 rule, the vast majority of time is likely spent on a small fraction of operations. Therefore, you first need to understand which part of the program consumes the most time. Specifically, we should try to optimize (parallelize) these parts of the code. If you optimize code that only takes up 1% of the execution time, even if you optimize it to the extreme where its runtime becomes zero, your overall gain will be negligible.

Of course, you need tools: a **profiler**, which is used to sample the execution of the state machine. "Dense" sampling can provide a sequence of where the program's time is spent.

> In software engineering, **profiling** ("program profiling", "software profiling") is a form of dynamic program analysis that measures, for example, the space (memory) or time complexity of a program, the usage of particular instructions, or the frequency and duration of function calls. Most commonly, profiling information serves to aid program optimization.

For example, the Linux `perf` tool is a powerful performance analysis tool that provides a suite of features for analyzing program performance and tracing system events. This tool is part of the kernel and utilizes the performance counter subsystem within the Linux kernel. `Perf` can help developers and system administrators monitor the performance of the entire system, including both hardware and software levels. The tool can measure software events like function calls and program execution time, and it can also monitor hardware events such as CPU cycles, instruction counts, and cache hits/misses. This makes it extremely suitable for performance tuning and bottleneck identification. Furthermore, `perf` supports real-time event tracing, allowing it to record and report various events during system operation, such as context switches, system calls, and page faults. These capabilities make `perf` an essential tool for performance analysis and problem diagnosis in Linux systems.


![perf](perf-top.gif)