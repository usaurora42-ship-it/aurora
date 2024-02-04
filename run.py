# encoding: utf-8
import sys
import pytest
from app import FlaskApp

# environment
environment = sys.argv[1] if len(sys.argv) > 1 else 'development'

if __name__ == "__main__":
    pass
    # manager.run()