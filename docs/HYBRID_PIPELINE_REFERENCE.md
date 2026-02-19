# AI_26 System: Comprehensive Analysis of Techniques

## 🧮 **Token Management**

### **Token Estimation Method:**
- **Library**: Custom implementation using regex pattern matching
- **Method**: `_TOKEN_RE = re.compile(r"\w+|[^\w\s]", re.UNICODE)` - counts words and punctuation
- **Function**: `estimate_tokens(text: str) -> int` in `token_utils.py`
- **Purpose**: Calculate token usage before sending to models to enforce limits

### **Token Controls:**
- **Context Window**: 6000 tokens maximum (hard cap defined in config)
- **Per-User Limits**: 50,000 tokens per day (configurable in `config.yaml`)
- **Rate Limiting**: 20 requests per minute per user
- **Safety Margin**: Additional tokens reserved for model responses

### **Advanced Token Techniques:**
- **Truncation**: `truncate_to_tokens(text: str, max_tokens: int) -> str` - Binary search for exact token count
- **Segment Trimming**: `trim_segments_to_limit(segments: List[str], max_tokens: int) -> List[str]` - Prioritized content inclusion
- **Message Estimation**: `estimate_messages_tokens(messages: Iterable[tuple[str, str]]) -> int` - Accounts for role overhead

## 📄 **Structured Output (JSON Mode)**

### **Implementation:**
- **QA Test Cases**: Uses structured prompt engineering for JSON output
- **Prompt Template**: Defined in `config.yaml` under `prompts.qa_testcase`
- **Format Requirements**: Explicitly specifies JSON array with specific fields (id, title, preconditions, steps, expected, priority)
- **Output Validation**: Relies on model's ability to follow structured format

### **Example Prompt:**
```
"You are a QA Test Case Generator. Produce a JSON array of test cases.
Each item must include: id, title, preconditions, steps, expected, priority.
Focus on functional behavior and edge cases. Output only valid JSON."
```

## 📉 **Quantization (Model Size Optimization)**

### **Current Implementation:**
- **Ollama Models**: Uses quantized models (e.g., `qwen2.5-coder:7b` with `Q4_K_M` quantization)
- **Embedding Model**: `nomic-embed-text` with quantization
- **Memory Efficiency**: Ollama handles quantization internally for CPU optimization
- **Performance Trade-offs**: Balanced between accuracy and speed for local inference

### **Quantization Benefits:**
- **Reduced Memory**: Quantized models use less RAM
- **Faster Inference**: Lower precision arithmetic is faster
- **CPU Optimization**: Designed for CPU-only inference on consumer hardware

## 🧠 **System Prompt Engineering**

### **Multi-Prompt Strategy:**
- **Main System Prompt**: "You are a precise assistant for a Telegram knowledge bot. Be concise, factual, and structured."
- **Summary Prompt**: "Summarize the conversation for future context. Keep it short, factual, and user-specific."
- **QA Test Case Prompt**: Structured prompt for JSON test case generation

### **Prompt Assembly:**
- **Context Building**: Dynamically assembles summary + recent messages + RAG context + user query
- **Section Markers**: Uses clear delimiters like `[Summary]`, `[Recent Messages]`, `[Relevant Context]`
- **Prioritization**: Orders components by importance and truncates to fit token limits

## 🕵️ **RAG (Retrieval-Augmented Generation)**

### **Embedding Method:**
- **Model**: `nomic-embed-text` via Ollama
- **Dimension**: 768-dimensional vectors
- **Encoding**: Sentence-transformers compatible embeddings

### **Chunking Strategy:**
- **Size**: 500 tokens per chunk (configurable)
- **Overlap**: 50 tokens overlap between chunks (configurable)
- **Method**: Token-based splitting preserving semantic boundaries
- **Purpose**: Balance retrieval precision with context coherence

### **Vector Database:**
- **System**: ChromaDB
- **Storage**: Persistent local storage in `backend/data/chroma/`
- **Indexing**: User-specific collections for data isolation
- **Query Method**: Cosine similarity search

### **Retrieval Process:**
- **Top-K**: Retrieves top 3 most relevant chunks (configurable)
- **Filtering**: User-specific filtering to maintain isolation
- **Scoring**: Similarity-based ranking
- **Limit**: Maximum 3 chunks returned to maintain context limits

## 🪟 **Sliding Window Technique**

### **Implementation:**
- **Recent Messages**: Keeps only last 3 message pairs (configurable via `recent_messages: 3` in config)
- **Dynamic Truncation**: `trim_segments_to_limit()` function implements sliding window
- **Context Preservation**: Maintains most recent context while discarding older content
- **Token Management**: Automatically adjusts window size based on token limits

### **Window Components:**
1. **Summary**: Latest conversation summary
2. **Messages**: Most recent 3 exchanges
3. **RAG Context**: Top 3 retrieved document chunks
4. **Current Query**: User's latest question

## 📐 **Context Window Limit**

### **Enforcement:**
- **Hard Cap**: 6000 tokens total (configurable in `max_context_tokens: 6000`)
- **Component Limits**: Each section contributes to total limit
- **Dynamic Adjustment**: `trim_segments_to_limit()` ensures compliance
- **Safety Buffer**: Reserve tokens for model response

### **Limit Management:**
- **Pre-emptive Truncation**: Trims content before sending to model
- **Priority-Based**: Critical context (user query) gets priority
- **Overflow Handling**: Graceful degradation when limits exceeded

## 📝 **Summary Trick**

### **Implementation:**
- **Continuous Summarization**: Updates conversation summary after each exchange
- **Context Compression**: Condenses entire conversation history into brief summary
- **Memory Efficiency**: Replaces full history with concise summary
- **Continuity**: Preserves important context without token bloat

### **Process:**
1. **Extract Recent Messages**: Gets last N exchanges
2. **Combine with Previous Summary**: Creates context for summarization
3. **Generate New Summary**: Uses AI to create compressed version
4. **Store for Future Use**: Saves summary for next interaction

## 🏷️ **Tag Trick**

### **Implementation:**
- **Section Markers**: Uses clear labels like `[Summary]`, `[Recent Messages]`, `[Relevant Context]`
- **Context Delimitation**: Explicit boundaries between different content types
- **Model Guidance**: Helps AI understand content structure
- **Information Hierarchy**: Establishes importance levels for different sections

### **Tag Examples:**
- `[Summary]\n` - Conversation history summary
- `[Recent Messages]\n` - Latest exchanges
- `[Relevant Context]\n` - Retrieved document snippets
- `[User Question]\n` - Current query

## 🔄 **Cloud Fallback & Quota Management**

### **Qwen Portal Integration:**
- **OAuth Authentication**: Reads credentials from `~/.qwen/oauth_creds.json`
- **Performance-Based Fallback**: Switches to cloud if local response > 30 seconds
- **Token Tracking**: Separate counters for local vs cloud usage
- **Quota Management**: Configurable daily limits to prevent 429 errors

### **Quota Optimization:**
- **Rate Limiting**: Configurable requests per minute
- **Conservative Limits**: Reduced max_tokens (4096 vs 8192) to preserve quota
- **Usage Monitoring**: Real-time tracking of API consumption
- **Fallback Suspension**: Stops cloud usage when approaching limits

## 🏗️ **Additional Architectural Elements**

### **Database Management:**
- **SQLite**: For metadata, user data, and token tracking
- **Schema**: Users, messages, documents, token usage logs
- **Isolation**: Per-user data separation
- **Persistence**: Local file-based storage

### **User Management:**
- **Isolation**: Separate document collections per user
- **Rate Limiting**: Per-user request and token limits
- **Authentication**: User ID-based (no complex auth in current version)
- **Session**: Stateless design with user ID in each request

### **Quality Controls:**
- **Response Validation**: Length limits and content filtering
- **Performance Monitoring**: Response times and token usage tracking
- **Error Handling**: Graceful degradation and fallback mechanisms
- **Resource Management**: Efficient memory and CPU usage

This comprehensive architecture provides a robust, scalable system that balances local privacy with cloud performance, maintains strict token controls, and implements sophisticated RAG capabilities for knowledge-based question answering while managing cloud quotas effectively.