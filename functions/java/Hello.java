/*package example;*/

/*import com.amazonaws.services.lambda.runtime.Context;*/

public class Hello {
    public String myHandler(int myCount, /*Context*/ Object context) {
        return String.valueOf(myCount);
    }

    public final static void main(String[] args)
    {
        System.out.println(new Hello().myHandler(10, null));
    }
}
