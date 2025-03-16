docker build -t ai_agent .

# 2) Run the container
docker run --rm -it \
  -v /Users/fuzzzer/programming/AI_tools/agentic_ai/playground:/app/playground \
  -p 1234:1234 \
  --name sandboxed_agent \
  ai_agent