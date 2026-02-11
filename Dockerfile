FROM python:3.11-slim

LABEL maintainer="CruxLabx <kaliyugiheart@gmail.com>"
LABEL description="MOL Playground — Online compiler for the MOL programming language"

WORKDIR /app

# Install dependencies first (cache layer)
COPY pyproject.toml ./
RUN pip install --no-cache-dir lark>=1.1.0 fastapi uvicorn

# Copy MOL source
COPY mol/ ./mol/
COPY playground/ ./playground/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "playground.server:app", "--host", "0.0.0.0", "--port", "8000"]
