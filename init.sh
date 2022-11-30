git clone https://github.com/pytorch/examples.git
python examples/super_resolution/main.py --upscale_factor 3 --batchSize 64 --testBatchSize 100 --nEpochs 500 --lr 0.001 --cuda

# 4h training -(256x256)-> 3.5h training
# cmp (256x256) effect -> no difference
# cmp (1epoch) effect 1.5h -> almost same

# --batch-size 8+
# python examples/fast_neural_style/neural_style/neural_style.py train ... --batch-size 6
