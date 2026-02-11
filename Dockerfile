FROM python:3.12-slim

LABEL maintainer="CruxLabx <kaliyugiheart@gmail.com>"
LABEL description="MOL — The Cognitive Programming Language"
LABEL version="0.4.0"

WORKDIR /app

# Install dependencies (cache layer)
COPY pyproject.toml ./
RUN pip install --no-cache-dir lark>=1.1.0 fastapi uvicorn

# Copy MOL source, playground, examples, and entrypoint
COPY mol/ ./mol/
COPY playground/ ./playground/
COPY examples/ ./examples/
COPY docker-entrypoint.sh ./

RUN chmod +x docker-entrypoint.sh

# Make mol CLI available globally
RUN pip install --no-cache-dir -e .

EXPOSE 8000

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["playground"]
