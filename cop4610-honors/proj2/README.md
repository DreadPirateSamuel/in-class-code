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
> The model file is large (\~500MB), so you need to download it into the project directory manually . This file will not be tracked by git, nor will it be uploaded to the server.

We provide a Python script, `chat.py`, which allows you to directly input a piece of text, perform tokenization, and then call the `gpt` command-line tool for completion. Yes, you are actually using a large language model that can generate text in this project\! The code has been fully prepared for you and works out of the box. In the example below, the number sequence "31373 612" corresponds to "Ladies and". As you can see, the language model has indeed generated readable text for us:



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

During Online Judge evaluation, `k≤4`. For real-world neural network training/inference systems, massively parallel processors like GPUs, which use a SIMT architecture, have a huge advantage over CPUs in terms of energy efficiency. Recalling the discussion on SIMT in the course, a warp of threads shares a single Program Counter, controlling multiple threads to execute instructions "in sync." In this scenario, for loading/storing large matrices and vectors, a single warp will generate a very long memory load (coalesced memory access). GPUs are also specially optimized for this memory access pattern—compared to the memory hierarchy designed for "logical programs" in CPUs, they have a much higher circuit and energy efficiency ratio.

In this project, you need to statically allocate threads (e.g., 4 workers), which will then complete the computational tasks. The threading library used during Online Judge testing is identical to the one in your project code.