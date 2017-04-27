import java.net.URL;
import java.net.URLClassLoader;
import java.net.MalformedURLException;
import java.lang.reflect.Method;
import java.lang.reflect.Parameter;
import java.lang.reflect.InvocationTargetException;
import java.util.List;
import java.util.ArrayList;

class FunctionLoader
{
	private Method function = null;
	private Object object = null;
	private boolean debug = false;

	public FunctionLoader(boolean debug)
	{
		this.debug = debug;
	}

	private void logfail(String context, String s)
	{
		System.err.println("ERROR: [" + String.format("%12s", context) + "] " + s);
	}

	private void debug(String context, String s)
	{
		System.out.println("DEBUG: [" + String.format("%12s", context) + "] " + s);
	}

	public void load(String classname, String methodname)
	{
		URL url = null;
		try
		{
			url = new URL("file://./" + classname + ".class");
		}
		catch(MalformedURLException e)
		{
			this.logfail(classname, "Inaccessible function: " + e.toString());
			return;
		}
		URL[] urls = {url};
		URLClassLoader loader = new URLClassLoader(urls);

		Class plc = null;
		try
		{
			plc = Class.forName(classname, true, loader);
		}
		catch(ClassNotFoundException e)
		{
			this.logfail(classname, "Invalid function: " + e.toString());
			return;
		}

		Object plo = null;
		try
		{
			plo = plc.newInstance();
		}
		catch(InstantiationException|IllegalAccessException e)
		{
			this.logfail(classname, "Function initialisation failure: " + e.toString());
			return;
		}

		Method method = null;
		//try
		{
			//method = plc.getMethod(methodname, Object.class, Object.class);
			//method = plc.getMethod(methodname, new Class[]{});
			Method[] methods = plc.getMethods();
			for(Method cmethod : methods)
			{
				if(methodname.equals("SCAN"))
				{
					if((!cmethod.getName().equals("wait"))
					&& (!cmethod.getName().equals("equals"))
					&& (!cmethod.getName().equals("toString"))
					&& (!cmethod.getName().equals("hashCode"))
					&& (!cmethod.getName().equals("getClass"))
					&& (!cmethod.getName().equals("notify"))
					&& (!cmethod.getName().equals("notifyAll")))
					{
						Parameter[] parameters = cmethod.getParameters();
						String params = "";
						for(Parameter p : parameters)
							params += " " + p.getName();
						System.out.println(cmethod.getName() + params);
					}
				}
				else if(cmethod.getName().equals(methodname))
				{
					method = cmethod;
				}
			}
		}
		/*catch(NoSuchMethodException e)
		{
			this.logfail(classname, "Method assignment failure: " + e.toString());
			return;
		}*/

		if(method != null)
		{
			this.object = plo;
			this.function = method;
		}
	}

	public void exec(Object[] parametervalues)
	{
		String functionname = this.function.getName();

		Parameter[] parametertypes = this.function.getParameters();

		debug(functionname, this.function.toString());
		debug(functionname, parametertypes.toString());
		for(Parameter p : parametertypes)
			debug(functionname, p.toString());

		if(parametervalues.length != parametertypes.length)
		{
			this.logfail(functionname, "Non-matching parameter count.");
		}

		List<Object> parameterlist = new ArrayList<Object>();
		for(int i = 0; i < parametervalues.length; i++)
		{
			Object p = parametervalues[i];
			if(parametertypes[i].getType() == int.class)
				p = Integer.parseInt((String)p);
			parameterlist.add(p);
		}
		Object[] parameters = parameterlist.toArray();

		Object result = null;
		try
		{
			result = this.function.invoke(this.object, parameters);
		}
		catch(IllegalAccessException|InvocationTargetException e)
		{
			this.logfail(functionname, "Method invocation failure: " + e.toString());
			return;
		}

		System.out.println(result);
	}
}

public class JavaExec
{
	public JavaExec()
	{
	}

	public void init(String classname, String methodname, Object[] parametervalues)
	{
		FunctionLoader fl = new FunctionLoader(false);
		fl.load(classname, methodname);
		if(!methodname.equals("SCAN"))
		{
			fl.exec(parametervalues);
		}
	}

	public final static void main(String[] args)
	{
		ArrayList<String> params = new ArrayList<String>();
		for(int i = 2; i < args.length; i++)
			params.add(args[i]);

		JavaExec exec = new JavaExec();
		exec.init(args[0], args[1], params.toArray());
	}
}
