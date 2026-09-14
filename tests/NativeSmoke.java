public final class NativeSmoke {
    static { System.loadLibrary("jdk26smoke"); }
    private static native long add(long first, long second);
    public static void main(String[] args) {
        if (add(0x100000000L, 7L) != 0x100000007L) throw new AssertionError("JNI 64-bit result");
        System.out.println("JNI_SMOKE_OK");
    }
}
