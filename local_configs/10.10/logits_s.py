_base_ = [
    '../_base_/datasets/ade20k.py',
    '../_base_/default_runtime.py',
    '../_base_/schedules/schedule_160k.py'
]

norm_cfg = dict(type='SyncBN', requires_grad=True)

model = dict(
    type='SDModule',
    cfg_s=dict(
        type='EncoderDecoder',
        pretrained='pretrained/mit_b0.pth',
        backbone=dict(
            type='mit_b0',
            style='pytorch'),
        decode_head=dict(
            type='SegFormerHead',
            in_channels=[32, 64, 160, 256],
            in_index=[0, 1, 2, 3],
            feature_strides=[4, 8, 16, 32],
            channels=128,
            dropout_ratio=0.1,
            num_classes=150,
            norm_cfg=norm_cfg,
            align_corners=False,
            decoder_params=dict(embed_dim=256),
            loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
        ),
    cfg_t=dict(
        type='EncoderDecoder',
        backbone=dict(
            type='mit_b4',
            style='pytorch'),
        decode_head=dict(
            type='SegFormerHead',
            in_channels=[64, 128, 320, 512],
            in_index=[0, 1, 2, 3],
            feature_strides=[4, 8, 16, 32],
            channels=128,
            dropout_ratio=0.1,
            num_classes=150,
            norm_cfg=norm_cfg,
            align_corners=False,
            decoder_params=dict(embed_dim=768),
            loss_decode=dict(type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0))
    ),
    distillation = [
        {'student_layer':'decode_head.linear_pred',
        'teacher_layer':'decode_head.linear_pred',
        'loss_name':'KLDLoss',
        'loss_config':{
            'weight':1,
            'tau':1,
            'reshape_config':'logits',
            'resize_config':{'mode':'bilinear','align_corners':False},
            'mask_config':False,
            'transform_config':{'loss_type':'spatial','kernel_size':1,'stride':1},
            'ff_config':False
            },
        },
    ],
    s_pretrain = './pretrained/mit_b0.pth', # 学生的预训练模型
    t_pretrain = './pretrained/segformer.b4.512x512.ade.160k.pth',  # 老师的预训练模型
    train_cfg=dict(),
    test_cfg=dict(mode='whole'),
)
optimizer = dict(_delete_=True, type='AdamW', lr=0.00006, betas=(0.9,0.999), weight_decay=0.01,
                paramwise_cfg=dict(custom_keys={'pos_block': dict(decay_mult=0.),
                                                 'norm': dict(decay_mult=0.),
                                                 'head': dict(lr_mult=10.)
                                                 }))

lr_config = dict(_delete_=True, policy='poly',
                 warmup='linear',
                 warmup_iters=1500,
                 warmup_ratio=1e-6,
                 power=1.0, min_lr=0.0, by_epoch=False)

log_config = dict(  
    interval=50, 
    hooks=[
        # dict(type='TensorboardLoggerHook') 
        dict(type='TextLoggerHook')
    ])
work_dir = '/apdcephfs/private_inchzhang/shared_info/logits_s'
data = dict(samples_per_gpu=2)
evaluation = dict(interval=16000, metric='mIoU')  
# resume_from = ''
