using System;

namespace StackDemo
{
    class Program
    {
        static void Main()
        {
            var stack = new MyStack<int>();
            stack.Push(10);
            stack.Push(20);
            stack.Push(30);
            stack.Push(20);
            stack.Push(40);

            Console.WriteLine("=== 初始栈 ===");
            stack.Print();

            Console.WriteLine("\n=== 删除第一个 20 ===");
            bool found = stack.Delete(20);
            Console.WriteLine("删除" + (found ? "成功" : "失败"));
            stack.Print();

            Console.WriteLine("\n=== 删除所有 40 ===");
            int count = stack.DeleteAll(40);
            Console.WriteLine("删除了 " + count + " 个元素");
            stack.Print();

            Console.WriteLine("\n=== 出栈 ===");
            int top = stack.Pop();
            Console.WriteLine("出栈元素: " + top);
            stack.Print();

            Console.WriteLine("\n=== 测试删除不存在的元素 ===");
            found = stack.Delete(99);
            Console.WriteLine("删除 99: " + (found ? "找到" : "未找到"));

            Console.WriteLine("\n=== 清空测试 ===");
            stack.DeleteAll(10);
            stack.DeleteAll(30);
            Console.WriteLine("清空后栈是否为空: " + stack.IsEmpty);
        }
    }
}
