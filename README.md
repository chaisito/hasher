# Hasher - Fb32
Simple python hash algorithm based on logic gates operations

# How Does It Work?

## State
```
def fb32(text):
    state = [
        0x243F6A88,
        ...
    ]
  ```
We have 8 numbers, where each number is 32 bits

>[!Note]
> _We have `8 x 32 = 256`, which means that (conceptually) each hash will own 8 different internal registers, these registers are what actually get scrambled when creating the hash_

## Convertion of Text to Bytes
Suppose we hash the word
`tomato`

Internally we process all 6 characters as:
```
01110100
01101111
01101101
01100001
01110100
01101111
```
> The character values are processed one byte at a time

## Expanding the Byte
Since we are working with `32-bit` values, we have to convert our `8-bit` character
### From
`01110100`

### To Something Like
`01110100 01110100 01110100 01110100`

#### For example
Letter "a" `97 = 0x61` becomes `0x61616161` _Now our input can interact with all 32 bits of a register_

## Position
In the code we have

`message ^= position * 0x9E3779B1` _Which multiplies the actual position of a character by 2654435761_

>[!Note]
>`0x9E3779B1` is the hexadecimal form of **2654435761** this number is used for its relation to the _Golden Ratio_ and its tendency of distributing `32-bit` values smoothly 

This prevents repeated letters entering the "circuit" identically

#### As an Example
`aaaa` would be hashed as `0x61616161`

Instead the process is:
```
a @ position 0
a @ position 1
a @ position 2
a @ position 3
```
So every letter enters uniquely

<img width="91.5" height="121.5" alt="Fb32-position-diagram" src="https://github.com/user-attachments/assets/e5e6f0a8-1f38-40a7-95c3-b8a837a441e0" />

This makes `ab` and `ba` behave completely different

## Choose
In the code we have the following function
```
def choose(a, b, c):
    return XOR(
        AND(a, b),
        AND(NOT(a), c)
    )
```
Which describes our first gate

At a one-bit level that would look something like:
```
a = 1
b = 0
c = 1
```

### Step by Step
Firstly
```
a AND b

1 AND 0 = 0
```

Then
```
NOT a AND c

NOT 1 = 0
0 AND 1 = 0
```

Then
```
0 XOR 0 = 0
```

Graphically it should look something like:

<img width="481.5" height="211.5" alt="Fb32-choose-diagram" src="https://github.com/user-attachments/assets/b086a04b-6b57-4d9a-9ebe-f7f64589e7de" />
⠀


> This is done with 32 bits at the same time

## Majority
The second gate entered is described in the code as
```
def majority(a, b, c):
  ...
```

At each bit position

<img width="245.5" height="167.5" alt="Fb32-majority-table" src="https://github.com/user-attachments/assets/48db1e39-5ca2-45f6-b219-36d93c6bee7f" />
⠀


> If at least two inputs are 1 the output shall be 1

The **circuit** ends up being

<img width="511.2" height="391.5" alt="Fb32-majority-diagram" src="https://github.com/user-attachments/assets/7b7affde-5211-45b4-8dbc-97f27c537441" />

⠀

>[!Important]
> This is useful because bits coming from several registers can influence the result

## Parity
After **CHOOSE** gate
```
def parity(a, b, c):
    return XOR(XOR(a, b), c)
```

So for each bit

<img width="245.5" height="167.5" alt="Fb32-partity-table" src="https://github.com/user-attachments/assets/10305613-8dbe-423e-ba6a-7222055ce89d" />

This detects whether an odd number of inputs are 1
> Useful for diffusion since XOR operator is quite sesitive to bit changes

## First Gate Layer <img width="25" height="25" alt="juan" src="https://github.com/user-attachments/assets/17057a69-275c-495b-9364-45765f6e85c4" />
Inside every round we have
```
g1 = choose(A, B, C)
g2 = majority(D, E, F)
g3 = parity(G, H, message)
```

This can be visualized as parallel circuits

<img width="271.5" height="151.5" alt="Fb32-first_layer-diagram" src="https://github.com/user-attachments/assets/7a4b660a-55f6-4550-9b84-e7ce023eb523" />

Where `M` is our message word, here now different states have been combined

## Rotation <img width="25" height="20" alt="im-only-human-im-only-human-after-all" src="https://github.com/user-attachments/assets/b0916992-83d4-44c4-8928-246a6e973511" />
After the **First Layer** is complete, we enter **Rotation**
```
p1 = ROTL(g1, 3)
p2 = ROTL(g2, 7)
p3 = ROTL(g3, 13)
```
>[!Important]
>This **DOES NOT** change how many 1 or 0 are present, it changes **WHERE** they are connected

In the case where we have 8 bits
```
10110001
```

They get to be rotated to the left by 3
```
10001101
```

Conceptually, it ends up being like crossing wires

<img width="181.5" height="151.5" alt="Fb32-rotation-diagram" src="https://github.com/user-attachments/assets/18ecaed8-1750-40a3-9636-e6ceca991b51" />

⠀

This is why rotation is useful in ***Hash*** algorithms

Without **Rotation** `bit 0` would be interacting with itself indefinitely

However, with rotation

<img width="61.5" height="211.5" alt="Fb32-ROTL-interaction-diagram" src="https://github.com/user-attachments/assets/c1c89dbf-fcee-474d-8c99-d523c3a3ec89" />

⠀

Eventually, influencing many positions

## Second Gate Layer <img width="25" height="25" alt="dva" src="https://github.com/user-attachments/assets/68263395-60e2-4867-8530-9d75997eb760" />
After **Rotation**
```
x1 = XOR(p1, p2)
x2 = XOR(p2, p3)
x3 = XOR(p3, p1)
```

This code can be seen as crossing the three branches we already have

<img width="241.5" height="391.5" alt="Fb32-second_layer-diagram" src="https://github.com/user-attachments/assets/f7439090-93b2-448c-9faf-ed2d88818163" />

⠀

Then we run them through the same gates again
```
y1 = choose(x1, C, F)
y2 = majority(x2, D, G)
y3 = parity(x3, E, H)
```

Now, we have

<img width="61.5" height="264.0" alt="Untitled Diagram drawio (6)" src="https://github.com/user-attachments/assets/293ad848-c297-4b3f-952d-3215da5f9b56" />

⠀

Here, diffusion starts

## Injection of Original Input
Here we have the following expression in code
```
y1 ^= message
```  
>The rotated versions of `message` go into `y2` and `y3`

Means that we are not letting the message dissapear ater just one operation  
The character influences other branches

<img width="271.5" height="151.5" alt="Fb32-injection-diagram" src="https://github.com/user-attachments/assets/c26999dc-0a84-4fd7-8f53-52cb3f8c9ce6" />  

This makes a single input bit to spread more agrresively

## Register Update
We create new registers
```
newA = ROTL(XOR(A, y1), 5)
```

Graphically

<img width="391.5" height="151.5" alt="Fb32-register_update-diagram" src="https://github.com/user-attachments/assets/a3c89bc5-02a8-4155-8230-f712c4900a7f" />

⠀
>The same happens with `B` and `C`

Then
```
newD = XOR(
    D,
    majority(newA, newB, newC)
)
```

`D` is now dependant of
* old D
* new A
* new B
* new C

Since each of those also depend on other registers, we have a network of dependencies  

## Avalanche <img width="20" height="20" alt="ffvii-avalanche-logo" src="https://github.com/user-attachments/assets/385e8d0a-328a-4a06-94bf-d922210074f0" />
Imagine changing one bit

`hello` versus `jello`

Initially, one character differs. However after the **First Gate Layer**, maybe several bits have changed.  
**Rotations** move those differences  
**XOR** sends them to other registers  
**Choose**, **Majority** and **Partity** combine them  

By now, after one round many more bits should have changed entirely  
After 24 rounds **about HALF of the 256 bits should differ**  

<img width="61.5" height="271.5" alt="Fb32-avalanche-diagram" src="https://github.com/user-attachments/assets/1220a054-4311-4ea6-baa9-1dd1a804cfb2" />

This is called the **Avalanche** effect

## Why 24 Rounds?
Here  

`for round_number in range(24):`

means that each input byte passes through the circuit 24 times  

One pass might not be able to spread the information quite enough
Several passes mean
1. A affects B
2. B affects C
3. C affects D  
   ...  
   eventually A affects basically everything

## Moving to the Next Character
So far we have only seen the operation made through the 8 bits of a single character 

Let us ***Hash*** the word `cat`

First we process completely the character `c`, this becomes **State<sub>1</sub>**  

Then `a` enters that changed State

<img width="151.5" height="121.5" alt="Fb32-next_char-diagram" src="https://github.com/user-attachments/assets/88867cb2-f023-40cd-ac02-45897fb06b48" />

⠀

Then `t`

<img width="151.5" height="121.5" alt="Fb32-next_char-diagram-2)" src="https://github.com/user-attachments/assets/6f24285d-43f7-4477-9822-eeccd360399f" />

⠀

So this process is now chained

<img width="90.75" height="271.5" alt="Fb32-next_char-diagram-FULL" src="https://github.com/user-attachments/assets/69433fea-db7b-4a01-8258-c7142f626789" />

⠀
This means that every later character depends on basically everything that has happened before it

## Turning the State into Text
At the end
```
return "".join(
    f"{value:08x}"
    for value in state
)
```

Each `32-bit` number becomes **8 hexadecimal characters**  

#### For example  

`A = 0x12AC74EF` becomes `12ac74ef`  
> 8 registers of `8x8 hex characters` gives us `64 hex characters`

Since one hex character represents 4 bits,  
`64 x 4 = 256 bits`  
Giving us a final ***Hash*** of length `256 bits`

## Complete Circuit
One round of the circuit looks like this

<img width="481.5" height="631.5" alt="Fb32-complete_circuit-diagram" src="https://github.com/user-attachments/assets/9ddf1537-9437-49e6-971d-38155c22669c" />

⠀

After many rounds

<img width="264.1" height="204.1" alt="Fb32-complete_circuit-diagram-AFTER" src="https://github.com/user-attachments/assets/a0577ae8-3352-4f3e-968d-e1eecb3fe234" />

⠀
⠀

**Special thanks to CyberTec team @ ITESM CEM**
