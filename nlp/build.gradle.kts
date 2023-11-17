plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
}

android {
    namespace = "com.ressphere.nlp"
    compileSdk = 33

    defaultConfig {
        minSdk = 30

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
        consumerProguardFiles("consumer-rules.pro")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "proguard-rules.pro"
            )
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_1_8
        targetCompatibility = JavaVersion.VERSION_1_8
    }
    kotlinOptions {
        jvmTarget = "1.8"
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.9.0")
    implementation("androidx.appcompat:appcompat:1.6.1")
    implementation("com.google.android.material:material:1.10.0")
    implementation("com.google.mlkit:smart-reply:17.0.2")
    implementation("com.google.mlkit:entity-extraction:16.0.0-beta4")
    // Use this dependency to use the dynamically downloaded model in Google Play Services
    implementation("com.google.android.gms:play-services-mlkit-smart-reply:16.0.0-beta1")
    implementation("org.tensorflow:tensorflow-lite-task-text:0.3.0")
    implementation("org.tensorflow:tensorflow-lite-gpu:2.9.0")


//    implementation("org.openjfx:javafx-controls:11.0.2")
//    implementation("edu.stanford.nlp:stanford-corenlp:4.5.5") {
//        exclude(module="junit")
//    }
//    implementation("edu.stanford.nlp:stanford-corenlp:4.5.5:models") {
//        exclude(module="junit")
//    }
//    implementation(files("libs/stanford-corenlp-4.5.5-models.jar"))

    // Gson library
    implementation("com.google.code.gson:gson:2.9.0")
    implementation("com.google.guava:guava:28.1-android")
    testImplementation("junit:junit:4.13.2")

    androidTestImplementation("androidx.test.ext:junit:1.1.5")
    androidTestImplementation("androidx.test.espresso:espresso-core:3.5.1")

    // Exclude the conflicting class from the JAXB library
//    api(group = "com.sun.xml.bind", name = "jaxb-impl", version = "2.4.0-b180830.0438") {
//        exclude(group = "com.sun.xml.bind", module = "jaxb-core-2.3.0.1")
//    }
}