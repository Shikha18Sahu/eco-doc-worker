
import * as dotenv from 'dotenv';
dotenv.config();
// PDF LOAD
import { PDFLoader } from '@langchain/community/document_loaders/fs/pdf';
import { RecursiveCharacterTextSplitter } from '@langchain/textsplitters';
import { GoogleGenerativeAIEmbeddings } from '@langchain/google-genai';
import { Pinecone } from '@pinecone-database/pinecone';
import { PineconeStore } from '@langchain/pinecone';

async function indexDocument() {

  const PDF_PATH = './dsa.pdf';
const pdfLoader = new PDFLoader(PDF_PATH);
const rawDocs = await pdfLoader.load();

console.log("PDF loaded successfully with", rawDocs.length, "documents.");
//Chunking 
const textSplitter = new RecursiveCharacterTextSplitter({
    chunkSize: 1000,
    chunkOverlap: 200,
  });
const chunkedDocs = await textSplitter.splitDocuments(rawDocs);

console.log("Chunking completed. Number of chunks created:", chunkedDocs.length);
// console.log(chunkedDocs.length, 'chunks created');

// Vector Embedding model

const embeddings = new GoogleGenerativeAIEmbeddings({
    apiKey: process.env.GEMINI_API_KEY,
    model: 'text-embedding-004',
  });
 console.log("Embeddings model configured with model:", embeddings.modelName);
  // Database configuration
  // Initialize Pinecone client
  const pinecone = new Pinecone();
  const pineconeIndex = pinecone.Index(process.env.PINECONE_INDEX_NAME);

  console.log("Pinecone configured with index name:", process.env.PINECONE_INDEX_NAME);
 

// langchain (chunking,embedding, database)
await PineconeStore.fromDocuments(chunkedDocs, embeddings, {
    pineconeIndex,
    maxConcurrency: 5,
  });
  console.log("Data Stored in Pinecone successfully.");

}
indexDocument();