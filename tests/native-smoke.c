#include "NativeSmoke.h"
JNIEXPORT jlong JNICALL Java_NativeSmoke_add(JNIEnv *env, jclass type, jlong first, jlong second) {
    (void)env;
    (void)type;
    return first + second;
}
