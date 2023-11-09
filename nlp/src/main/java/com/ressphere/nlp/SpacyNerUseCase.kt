package com.ressphere.nlp

import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlin.coroutines.CoroutineContext

//import ai.huggingface:transformers:4.18.0
//import org.tensorflow.lite.*

//from datasets import load_dataset
//from transformers import pipeline
//
//if __name__ == '__main__':
//
//
//# Extract the NER model
//ner_model = pipeline("ner", model="dslim/bert-base-NER", tokenizer="dslim/bert-base-NER")
//
//# Example string
//example_string = "Amy is on the bus"
//
//# Use the NER model to extract entities from the example string
//ner_results = ner_model(example_string)
//
//# Display the results
//print(ner_results)

class SpacyNerUseCase(
    private val response: (ans: String)->Unit,
    private val scope: CoroutineScope,
    private val coroutineDispatchContext: CoroutineContext = Dispatchers.Default
) : NLPExecutor {

//    // Load the NER model
////    val nerModel = NerModel.create(NerConfig.create("dslim/bert-base-NER"))
//    var model  =
//        BertForTokenClassification.fromPretrained("dslim/bert-base-NER")
////    val nerModel = Pipeline.fromPretrained("dslim/bert-base-NER")
//
//    // Create a NerProcessor object
//   // val nerProcessor = NerProcessor(nerModel)
//
//    override fun execute(question: String) {
//        scope.launch(coroutineDispatchContext) {
//            val nerResults = nerProcessor.process(question)
//            var result = ""
//            for (nerResult in nerResults) {
//                result += "${nerResult.entityType}: ${nerResult.text}")
//            }
//            response(result)
//        }
//    }

    override fun close() {

    }
}