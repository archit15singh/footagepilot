# Audio input for reference editing

Research checked 14 November 2026. The goal is to interpret music, speech and sound effects in the actual reference soundtrack and compare them with the decoded picture. The audio-aware model provides semantic evidence. Local tools provide the timeline and candidate timestamps.

## First local pilot

**Run Qwen2.5-Omni-3B with llama.cpp and Beat This! on CPU.** llama.cpp lists the Qwen model as supporting audio and vision inputs. Its Q4_K_M weights are about 2.10 GB and the Q8 multimodal projector is about 1.54 GB. Their combined file size makes this a plausible pilot on the available 16 GB Mac. The local listening pilot below verifies WAV ingestion on this machine. Separate frame inputs and Beat This! remain follow-up evaluations. [llama.cpp multimodal support](https://github.com/ggml-org/llama.cpp/blob/master/docs/multimodal.md), [GGUF files](https://huggingface.co/ggml-org/Qwen2.5-Omni-3B-GGUF/tree/main), [Qwen model documentation](https://github.com/QwenLM/Qwen2.5-Omni)

Beat This! takes audio and returns separate beat and downbeat estimates, with a documented CPU execution path. Align both streams of estimates to the existing frame presentation timestamps and retain their signed differences. Keep audio-model descriptions such as an instrumental build, vocal entry or impact as hypotheses tied to bounded audio excerpts. [Beat This! inference](https://github.com/CPJKU/beat_this#inference), [research paper](https://arxiv.org/abs/2407.21658), [FootagePilot timing](REFERENCE-TIMING.md)

Gemma 4 E2B or E4B is a second small local comparator. Google's examples establish audio prompting and speech processing, with a documented 30-second clip limit. Its performance on music structure would need a separate test. NVIDIA Music Flamingo is more directly aimed at musical structure, timbre and lyrics. Its 8B model card lists Linux and NVIDIA A100/H100 as supported deployment hardware and a noncommercial license. [Gemma audio guide](https://ai.google.dev/gemma/docs/capabilities/audio), [Google llama.cpp deployment guide](https://github.com/google-gemma/docs/blob/main/docs/deployment/llamacpp.md), [Music Flamingo model card](https://huggingface.co/nvidia/music-flamingo-2601-hf)

**MOSS-Music-8B-Thinking is the specialist worth testing for sung lyrics and musical sections.** The model authors describe timestamped lyrics, beat and downbeat localization, and section boundaries. Their published lyrics error scores cover recognition, and the card says detailed timestamped ASR results are forthcoming. A 4-bit community MLX conversion is about 6 GB on disk. Its backend is an open upstream PR, and the conversion's logit comparison does not establish timing accuracy. [MOSS-Music model card](https://huggingface.co/OpenMOSS-Team/MOSS-Music-8B-Thinking), [4-bit MLX conversion](https://huggingface.co/mlx-community/MOSS-Music-8B-Thinking-4bit), [MLX backend PR](https://github.com/OpenMOSS/MOSS-Music/pull/3)

## Hosted comparison

| Model | Where it fits | Limits to test |
| --- | --- | --- |
| Gemini 3.5 Flash-Lite | Accepts audio, video and images. Google's audio guide documents non-speech recognition and timestamped segment questions. Use a short WAV and exact still frames when the cue involves a fast visual transition. | Default static video extracts one frame per second. The audio guide describes mono conversion. Native frame timestamps and stereo-sensitive cues should remain local. [Model](https://aistudio.google.com/docs/models/gemini-3.5-flash-lite), [audio guide](https://aistudio.google.com/docs/audio), [video guide](https://aistudio.google.com/docs/video-understanding) |
| OpenAI GPT-Audio-1.5 | Accepts raw WAV input through Chat Completions. A direct comparison for identifying what's audible in a short excerpt. | Its input modalities are text and audio. The documentation establishes ingestion. Accuracy for sung lyrics, downbeat placement and effect attribution remains unmeasured here. GPT-6.1 Sol in Codex does not accept audio input. [Audio guide](https://developers.openai.com/api/docs/guides/audio-chat-completions), [audio model](https://developers.openai.com/api/docs/models/gpt-audio-1.5), [Sol model](https://developers.openai.com/api/docs/models/gpt-6.1-sol) |

At Google's documented 32 audio tokens per second and Flash-Lite's paid rate of $0.30 per million input tokens, 16 minutes of audio would cost about $0.01 for the audio input. Prompts, images, output and repeat calls add cost. Google's terms also distinguish unpaid services that may use submitted content to improve products from paid services. No reel media was sent to a provider during this research. [Audio tokenization](https://aistudio.google.com/docs/audio#technical-details), [pricing](https://aistudio.google.com/docs/pricing#gemini-3.5-flash-lite), [terms](https://aistudio.google.com/docs/terms)

## How to verify the pilot

1. Use short audio clips with known events. Include a generated click track with known downbeats, silence, licensed sung material with an annotated vocal phrase, and a clip with a known effect over music.
2. Pair each audio clip with frame-accurate edit timestamps. Include one deliberately shifted version. Give neither model the answer key or the identity of the shifted clip.
3. Score cue classification and timing separately. At 30 fps, two frames are about 67 ms. Report both missed cues and false positives, including beat guesses in silence. A convincing explanation with an incorrect time is still a timing error.
4. Check one representative reel of each type after the controls, then expand. Let the existing frame ledger and beat tracker measure timing. Use the audio model to label what the cue may be, preserving uncertainty where sources overlap.

## Local listening pilot

A 16 GB Apple Silicon Mac ran llama.cpp b12383 with Qwen2.5-Omni-3B Q4_K_M and its Q8_0 projector. The server used one slot, a 4096-token context, and CPU projector execution. Keep the server on loopback and use a local API key when the server is running. [Pinned runtime](https://github.com/ggml-org/llama.cpp/releases/tag/b12383), [OpenAI-compatible audio request format](https://github.com/ggml-org/llama.cpp/blob/b12383/tools/server/README.md)

```sh
llama-server -m Qwen2.5-Omni-3B-Q4_K_M.gguf \
  --mmproj mmproj-Qwen2.5-Omni-3B-Q8_0.gguf \
  --no-mmproj-offload --host 127.0.0.1 --port 8080 -c 4096 --parallel 1 \
  --api-key "$FOOTAGEPILOT_AUDIO_API_KEY"

# In a second shell with the same key:
python3 -m footagepilot reference-listen projects/reference/analysis.json \
  --start 2.5 --end 8.5 --output projects/audio-note.json
```

The command verifies the source hash, extracts up to 15 seconds of mono PCM on the reference clock and sends a WAV to the local server. The JSON retains the excerpt bounds, source and audio hashes, the server's model name and its description. Treat the description as a hypothesis. Compare it with the spectrogram, frame timestamps and source material before using it to explain a cut.

The pilot transcribed a generated spoken sentence and recognized digital silence. A synthetic mix had repeating low pulses, sustained harmonics, a noise burst and a quiet tail. The model recognized the pulse and missed the other events. A real soundtrack excerpt from 2.5–8.5 s was recognized as music. In a second reel the model reported music without singing, while the local speech-recognition output contained candidate sung words. One excerpt exceeded the output limit. These outcomes leave detailed event coverage and source attribution open. Use the deterministic cue ledger to place events and retain uncertain source labels. [Reference timing](REFERENCE-TIMING.md)
