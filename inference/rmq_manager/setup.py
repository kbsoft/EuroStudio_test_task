from setuptools import setup, find_packages

setup(
    name="rmq_manager",
    version="1.0.0",
    description="RabbitMQ connection manager",
    install_requires=[
        "pika>=1.1.0",
        "retry>=0.9.2",
    ],
    packages=find_packages(),
    python_requires=">=3.6",
)
