# Big Data Project: Real-Time Twitter Sentiment Analysis Using Kafka, Spark (MLLib & Streaming), MongoDB and Django.

## Overview

This repository contains a Big Data project focused on real-time sentiment analysis of Twitter data (classification of tweets). The project leverages various technologies to collect, process, analyze, and visualize sentiment data from tweets in real-time.

## Project Architecture

The project is built using the following components:

- **Apache Kafka**: Used for real-time data ingestion from Twitter DataSet.
- **Spark Streaming**: Processes the streaming data from Kafka to perform sentiment analysis.
- **MongoDB**: Stores the processed sentiment data.
- **Django**: Serves as the web framework for building a real-time dashboard to visualize the sentiment analysis results.
- **chart.js** & **matplotlib** : for plotting.

- This is the project plan :
   ![project img](imgs/flow.png)

## Features

- **Real-time Data Ingestion**: Collects live tweets using Kafka from the Twitter DataSet.
- **Stream Processing**: Utilizes Spark Streaming to process and analyze the data in real-time.
- **Sentiment Analysis**: Classifies tweets into different sentiment categories (positive, negative, neutral) using natural language processing (NLP) techniques.
- **Data Storage**: Stores the sentiment analysis results in MongoDB for persistence.
- **Visualization**: Provides a real-time dashboard built with Django to visualize the sentiment trends and insights.


## Repository Structure

- **Django-Dashboard** : this folder contains Dashboard Django Application
- **Kafka-PySpark** : this folder contains kafka provider and pyspark streaming (kafka consumer).
- **ML PySpark Model** : this folder contains the trained model with jupyter notebook and datasets.
- **zk-single-kafka-single.yml** : Download and install Apache Kafka in docker.
- **bigdataproject rapport** : a brief report about the project (in french).




