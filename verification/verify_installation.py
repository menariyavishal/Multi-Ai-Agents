#!/usr/bin/env python
"""Verify installations"""

try:
    import flask
    print(f"✅ Flask {flask.__version__} installed")
except ImportError as e:
    print(f"❌ Flask: {e}")

try:
    import langchain
    print(f"✅ LangChain {langchain.__version__} installed")
except ImportError as e:
    print(f"❌ LangChain: {e}")

try:
    import langgraph
    print(f"✅ LangGraph installed")
except ImportError as e:
    print(f"❌ LangGraph: {e}")

try:
    import pymongo
    print(f"✅ PyMongo {pymongo.__version__} installed")
except ImportError as e:
    print(f"❌ PyMongo: {e}")

try:
    import pydantic
    print(f"✅ Pydantic {pydantic.__version__} installed")
except ImportError as e:
    print(f"❌ Pydantic: {e}")

try:
    import diskcache
    print(f"✅ DiskCache installed")
except ImportError as e:
    print(f"❌ DiskCache: {e}")

print("\n✅ All dependencies installed successfully!")
