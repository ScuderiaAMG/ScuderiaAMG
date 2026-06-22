/**
 * 【功能说明】
 * 本程序模拟了发牌（Deal）操作，演示了Java集合框架中List接口、
 * Collections工具类和List.subList()方法的用法。
 * 程序从命令行接收玩家数量和每手牌数，生成一副标准的52张扑克牌，
 * 洗牌后为每个玩家发指定数量的牌。dealHand方法使用subList视图
 * 从牌堆底部取牌，体现了"视图"操作对原集合的影响。
 *
 * 【知识点】
 * 1. List接口：有序集合，可包含重复元素
 * 2. ArrayList类：基于动态数组的List实现
 * 3. Collections.shuffle()：将集合中的元素随机打乱（洗牌算法）
 * 4. List.subList(fromIndex, toIndex)：返回原列表的一个"视图"（视图的修改会反映到原列表）
 * 5. 视图（View）的概念：subList返回的不是独立副本，而是原列表的视图
 * 6. 增强型for-each循环：for (String ss : suit) 简化数组/集合遍历
 * 7. 可变参数：args接收命令行参数
 * 8. 嵌套循环生成52张牌：外层花色 * 内层点数 = 4 * 13 = 52
 */
package chp5_advanced.exp5_13;                             // 声明包路径，该文件位于chp5_advanced.exp5_13包中

import java.util.ArrayList;                                // 导入ArrayList类，用于创建动态数组列表
import java.util.Collections;                              // 导入Collections工具类，提供shuffle等静态方法
import java.util.List;                                     // 导入List接口

class Deal_mimofixed {                                               // 主类（非public），模拟发牌操作
    public static void main(String args[]) {               // 主方法：程序执行的入口点
        int numHands = Integer.parseInt(args[0]);          // 从命令行参数获取玩家数量（第1个参数）
        int cardsPerHand = Integer.parseInt(args[1]);      // 从命令行参数获取每手牌数（第2个参数）

        // 创建一副标准的扑克牌（52张）
        String[] suit = new String[]{"spades", "hearts", "diamonds", "clubs"}; // 花色数组：黑桃、红心、方块、梅花
        String[] rank = new String[]{                      // 点数数组：A, 2~10, J, Q, K
            "ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "jack", "queen", "king"
        };
        List<String> deck = new ArrayList<String>();       // 创建空的牌堆列表（存放所有扑克牌）
        for (String ss : suit)                             // 外层循环：遍历4种花色
            for (String sr : rank)                         // 内层循环：遍历13种点数
                deck.add(sr + " of " + ss);                // 组合点数和花色，添加到牌堆中（如"ace of spades"）

        Collections.shuffle(deck);                         // 使用Collections工具类的shuffle方法洗牌（随机打乱牌的顺序）

        for (int i = 0; i < numHands; i++)                 // 循环遍历每个玩家
            System.out.println(dealHand(deck, cardsPerHand)); // 调用dealHand方法发牌并输出该玩家得到的牌
    }

    public static List<String> dealHand(List<String> deck, int n) { // 静态方法：从牌堆底部取出n张牌作为一手牌
        int deckSize = deck.size();                        // 获取当前牌堆的剩余牌数
        List<String> handView = deck.subList(deckSize - n, deckSize); // 使用subList获取牌堆底部n张牌的视图（注意：原方法名拼写为handView）
        List<String> hand = new ArrayList<String>(handView); // 通过视图创建一个新的ArrayList副本（独立的一手牌）
        handView.clear();                                  // 清空视图中的元素（同时也会从原列表deck中移除这些元素）
        return hand;                                       // 返回一手牌（副本）
    }
}
