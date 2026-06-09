using System;
using System.Collections.Generic;
using System.Linq;

namespace StackDemo
{
    /// <summary>
    /// 基于链表的泛型栈实现，支持 Push、Pop、Peek、Delete 操作
    /// </summary>
    public class MyStack<T>
    {
        private class Node
        {
            public T Data { get; set; }
            public Node? Next { get; set; }
            public Node(T data) => Data = data;
        }

        private Node? _top;
        private int _count;

        public int Count => _count;
        public bool IsEmpty => _count == 0;

        public void Push(T item)
        {
            var node = new Node(item) { Next = _top };
            _top = node;
            _count++;
        }

        public T Pop()
        {
            if (IsEmpty)
                throw new InvalidOperationException("Stack is empty.");
            T data = _top!.Data;
            _top = _top.Next;
            _count--;
            return data;
        }

        public T Peek()
        {
            if (IsEmpty)
                throw new InvalidOperationException("Stack is empty.");
            return _top!.Data;
        }

        /// <summary>
        /// 删除栈中第一个匹配的元素（从栈顶向下搜索）
        /// </summary>
        public bool Delete(T item)
        {
            if (IsEmpty) return false;

            if (EqualityComparer<T>.Default.Equals(_top!.Data, item))
            {
                _top = _top.Next;
                _count--;
                return true;
            }

            Node? current = _top;
            while (current.Next != null)
            {
                if (EqualityComparer<T>.Default.Equals(current.Next.Data, item))
                {
                    current.Next = current.Next.Next;
                    _count--;
                    return true;
                }
                current = current.Next;
            }
            return false;
        }

        /// <summary>
        /// 删除栈中所有匹配的元素
        /// </summary>
        public int DeleteAll(T item)
        {
            int removed = 0;

            while (_top != null && EqualityComparer<T>.Default.Equals(_top.Data, item))
            {
                _top = _top.Next;
                _count--;
                removed++;
            }
            if (_top == null) return removed;

            Node? current = _top;
            while (current.Next != null)
            {
                if (EqualityComparer<T>.Default.Equals(current.Next.Data, item))
                {
                    current.Next = current.Next.Next;
                    _count--;
                    removed++;
                }
                else
                {
                    current = current.Next;
                }
            }
            return removed;
        }

        public IEnumerable<T> ToEnumerable()
        {
            Node? current = _top;
            while (current != null)
            {
                yield return current.Data;
                current = current.Next;
            }
        }

        public void Print()
        {
            var elements = ToEnumerable().ToList();
            var joined = string.Join(", ", elements);
            Console.WriteLine("Stack (Count=" + Count + "): [" + joined + "]");
        }
    }
}
