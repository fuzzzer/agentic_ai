docker build -t ai_agent .

# 2) Run the container always use "/app" for docker starter
docker run --rm -it -t \
  -v /Users/fuzzzer/programming/AI_tools/agentic_ai/playground:/app \
  -p 1234:1234 \
  --name sandboxed_agent \
  ai_agent