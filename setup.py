from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define requirements directly in setup.py instead of reading from file
requirements = [
    "elasticsearch>=9.0.0",
    "pinecone-client>=2.0.0",
    "tqdm>=4.0.0",
    "python-dotenv>=0.15.0",
    "openai>=0.27.0",
    "numpy>=1.20.0"
]

setup(
    name="es-to-pinecone-transfer",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A pipeline to transfer documents from Elasticsearch to Pinecone with threading support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/es-to-pinecone-transfer",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.12.0",
            "black>=21.5b2",
            "isort>=5.9.1",
            "flake8>=3.9.2",
        ],
        "huggingface": [
            "sentence-transformers>=2.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "es-to-pinecone=es_to_pinecone_transfer.pipeline:main",
        ],
    },
)